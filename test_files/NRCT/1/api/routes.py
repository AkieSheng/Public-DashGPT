from flask import Blueprint, request, jsonify, send_file, stream_with_context, Response
import sqlite3
import os
from pathlib import Path
import json
import time
import traceback
from modules.agent import NewExplorationThread
from utils.sql import csv_to_sqlite

api_bp = Blueprint('api', __name__)

BASE_DIR = Path(__file__).parent.parent  # 主文件夹路径
DATABASES_DIR = BASE_DIR / "databases"  # 数据库存储路径
TABLES_DIR = BASE_DIR / "tables"  # 中间表存储路径
VA_STATES_DIR = Path(__file__).parent / "va_states"  # VA状态存储路径

for dir_path in [DATABASES_DIR, TABLES_DIR, VA_STATES_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)


def format_response(code=200, message="", data=None):
    """生成统一格式的JSON响应"""
    return jsonify({
        "code": code,
        "message": message,
        "data": data if data is not None else []
    })


def _state_path(va_id: str) -> Path:
    """获取VA系统状态文件的路径"""
    return VA_STATES_DIR / f"{va_id}.json"


def save_state(va_id: str, state: dict):
    """将VA系统状态保存到va_states目录"""
    state_path = _state_path(va_id)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_state(va_id: str) -> dict:
    """从va_states目录加载VA系统状态"""
    path = _state_path(va_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# 1. 上传数据库 POST /database
@api_bp.route('/database', methods=['POST'])
def upload_database():
    """处理数据库文件上传并解析表结构"""
    try:
        va_id = request.args.get('id')
        if not va_id:
            return format_response(400, "Missing ID parameter", None)
        if 'file' not in request.files:
            return format_response(400, "No file uploaded", None)

        file = request.files['file']
        if file.filename == '':
            return format_response(400, "Empty filename", None)

        os.makedirs('tables', exist_ok=True)
        os.makedirs(f'result/{va_id}', exist_ok=True)

        # 保存数据库
        db_path = DATABASES_DIR / f"{va_id}.db"
        file.save(str(db_path))

        if file.filename.endswith('.zip'):
            import zipfile
            csv_dir = DATABASES_DIR / f"{va_id}_csv"
            csv_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(str(db_path), 'r') as zip_ref:
                zip_ref.extractall(csv_dir)

            csv_to_sqlite(str(csv_dir), str(db_path))

            # 清理临时目录
            import shutil
            shutil.rmtree(csv_dir)

        try:
            # 使用NewExplorationThread初始化数据库分析
            exploration = NewExplorationThread(
                db_path=str(db_path),
                desc="",
                goal="",
                result_id=va_id,
                use_reflect=False,
                use_rag=False,
                models={}
            )

            # 执行数据库理解步骤
            exploration.current_stage_id = 0
            exploration._step()
            dataset = exploration.dataset
        except Exception as e:
            print(f"数据库处理错误: {str(e)}，使用备用方法")

            # 备用方法：直接处理数据库
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            database_info = []
            cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                cursor.execute(f'PRAGMA table_info({table_name})')
                columns = cursor.fetchall()

                table_info = {
                    'table': table_name,
                    'columns': []
                }

                for column in columns:
                    col_info = {
                        'column': column[1],
                        'dtype': column[2],
                        'description': f"字段 {column[1]}，类型为 {column[2]}"
                    }
                    table_info['columns'].append(col_info)

                database_info.append(table_info)

            dataset = {
                'tables': database_info,
                'description': f"数据库包含以下表: {', '.join([t[0] for t in tables])}"
            }

            conn.close()

            with open(f'result/{va_id}/0.txt', 'w', encoding='utf-8') as f:
                json.dump(dataset, f, ensure_ascii=False)

        # 保存VA系统基本信息
        va_info = {
            "id": va_id,
            "name": f"Visual Analytics System {va_id}",
            "created": int(time.time()),
            "dataset": dataset
        }
        save_state(va_id, va_info)

        # 构建返回体
        tables_data = []
        for table in dataset.get("tables", []):
            table_data = {
                "table": table.get("table", ""),
                "columns": []
            }

            for col in table.get("columns", []):
                table_data["columns"].append({
                    "column": col.get("column", ""),
                    "dtype": col.get("dtype", "")
                })

            tables_data.append(table_data)

        return format_response(200, "Database uploaded", tables_data)

    except Exception as e:
        print(traceback.format_exc())
        return format_response(500, f"Error processing database: {str(e)}", None)


# 2. 生成结果 POST /generate
@api_bp.route('/generate', methods=['POST'])
def generate_results():
    """生成VA系统各阶段内容并流式返回结果"""
    try:
        data = request.json
        if not data:
            return format_response(400, "无效的请求内容")
        va_id = data.get("id")
        if not va_id:
            return format_response(400, "缺少系统ID")

        os.makedirs(f'result/{va_id}', exist_ok=True)

        # 加载VA系统信息
        va_info = load_state(va_id)
        if not va_info:
            return format_response(404, "未找到VA系统")
        db_path = DATABASES_DIR / f"{va_id}.db"
        if not db_path.exists():
            return format_response(404, f"数据库文件不存在: {va_id}.db")
        # 获取请求参数
        desc = data.get("desc", "")
        goal = data.get("goal", "")
        initial_stage = data.get("initialStage", 0)
        max_steps = data.get("maxSteps", 10)
        use_reflect = data.get("useReflect", True)
        use_rag = data.get("useRag", False)

        # 获取模型配置
        model = data.get("model", "gpt-4o")  # 单一模型参数
        models = data.get("models", {})  # 多模型配置

        # 创建新版本的探索线程
        exploration = NewExplorationThread(
            db_path=str(db_path),
            desc=desc,
            goal=goal,
            result_id=va_id,
            max_steps=max_steps,
            use_reflect=use_reflect,
            use_rag=use_rag,
            model=model,
            models=models  # 传入多模型配置
        )

        # 设置初始阶段和数据
        if initial_stage > 0:
            exploration.current_stage_id = initial_stage
            # 根据初始阶段设置必要的数据
            if "dataset" in data:
                exploration.dataset = data["dataset"]
            else:
                exploration.dataset = va_info.get("dataset", {})
            if initial_stage > 1 and "requirements" in data:
                exploration.outputs["requirements"] = data["requirements"]
            if initial_stage > 2 and "tasks" in data:
                exploration.outputs["tasks"] = data["tasks"]
            if initial_stage > 3 and "plan" in data:
                # 与旧版兼容
                exploration.outputs["views"] = data["plan"].get("views", [])
                exploration.outputs["graph"] = data["plan"].get("graph", [])
                exploration.outputs["path"] = data["plan"].get("path", "")
            if initial_stage > 4 and "sqls" in data:
                exploration.outputs["sqls"] = data["sqls"]
            if initial_stage > 5 and "vlcodes" in data:
                exploration.outputs["vlcodes"] = data["vlcodes"]

        # 创建记录步骤输出的函数
        def record_step_output(step_num, output_content):
            """记录每个步骤的输出到文件"""
            output_file = Path(f'result/{va_id}/{step_num}.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_content, f, ensure_ascii=False)
            return output_file

        # 创建流式响应
        def generate():
            step = 0

            # 开始探索流程
            while exploration.current_steps < exploration.max_steps and exploration.current_stage_id < len(
                    exploration.stages):
                # 记录当前步骤前的状态
                prev_stage = exploration.current_stage_id
                prev_steps = exploration.current_steps

                # 执行当前步骤
                exploration._step()

                # 准备当前步骤的输出内容
                current_output = {
                    "stage": exploration.stages[prev_stage],
                    "stageId": prev_stage,
                    "outputs": {}
                }

                # 根据当前阶段添加相应输出
                if prev_stage == 0:  # DATABASE UNDERSTANDING
                    current_output["outputs"]["dataset"] = exploration.dataset
                elif prev_stage == 1:  # REQUIREMENT GENERATION
                    current_output["outputs"]["requirements"] = exploration.outputs.get("requirements", [])
                elif prev_stage == 2:  # TASK GENERATION
                    current_output["outputs"]["tasks"] = exploration.outputs.get("tasks", [])
                elif prev_stage == 3:  # PLAN GENERATION
                    current_output["outputs"]["views"] = exploration.outputs.get("views", [])
                    current_output["outputs"]["graph"] = exploration.outputs.get("graph", [])
                    current_output["outputs"]["path"] = exploration.outputs.get("path", "")
                elif prev_stage == 4:  # SQL GENERATION
                    current_output["outputs"]["sqls"] = exploration.outputs.get("sqls", [])
                    if exploration.outputs.get("sql_err_msg"):
                        current_output["outputs"]["sqlErrMsg"] = exploration.outputs.get("sql_err_msg")
                elif prev_stage == 5:  # VEGA-LITE GENERATION
                    current_output["outputs"]["vlcodes"] = exploration.outputs.get("vlcodes", {})

                # 记录步骤输出
                output_file = record_step_output(prev_steps, current_output)

                # 读取记录的输出文件
                try:
                    raw_content = output_file.read_text(encoding="utf-8") if output_file.exists() else ""
                except Exception as e:
                    print(f"读取步骤输出失败: {str(e)}")
                    raw_content = ""

                # 返回当前步骤结果
                response_data = {
                    "step": exploration.current_steps,
                    "raw": raw_content
                }
                step += 1

                yield json.dumps(response_data, ensure_ascii=False) + "\n"

            # 更新并保存最终VA状态
            va_info.update({
                "desc": desc,
                "goal": goal,
                "dataset": exploration.dataset
            })

            # 保存各阶段结果
            if "requirements" in exploration.outputs:
                va_info["requirements"] = exploration.outputs["requirements"]
            if "tasks" in exploration.outputs:
                va_info["tasks"] = exploration.outputs["tasks"]
            if "views" in exploration.outputs and "graph" in exploration.outputs and "path" in exploration.outputs:
                va_info["plan"] = {
                    "views": exploration.outputs["views"],
                    "graph": exploration.outputs["graph"],
                    "path": exploration.outputs["path"]
                }
            if "sqls" in exploration.outputs:
                va_info["sqls"] = exploration.outputs["sqls"]
            if "vlcodes" in exploration.outputs:
                va_info["vlcodes"] = exploration.outputs["vlcodes"]
            va_info['evaluation'] = exploration.evaluation_result
            save_state(va_id, va_info)

        return Response(stream_with_context(generate()), mimetype='application/json')

    except Exception as e:
        print(traceback.format_exc())
        return format_response(500, f"生成过程出错: {str(e)}")


# 3. 保存修改结果 POST /save
@api_bp.route('/save', methods=['POST'])
def save_results():
    """保存修改后的VA系统信息"""
    try:
        data = request.json
        if not data:
            return format_response(400, "无效的请求内容")
        va_id = data.get("id")
        if not va_id:
            return format_response(400, "缺少系统ID")
        va_info = load_state(va_id)
        if not va_info:
            return format_response(404, "未找到VA系统")

        # 更新提交的字段
        for key in data:
            if key != "id":  # 不更新ID
                va_info[key] = data[key]

        save_state(va_id, va_info)

        return format_response(200, "Saved", None)

    except Exception as e:
        return format_response(500, f"保存失败: {str(e)}")


# 4. 获取CSV文件 GET /
@api_bp.route('/', methods=['GET'])
def get_csv_file():
    """返回指定的CSV文件"""
    try:
        name = request.args.get('name')
        if not name or not name.endswith('.csv'):
            return format_response(400, "无效的文件名")

        file_path = TABLES_DIR / name
        if not file_path.exists():
            return format_response(404, "文件不存在")

        return send_file(str(file_path))

    except Exception as e:
        return format_response(500, f"获取文件失败: {str(e)}")


# 5. 获取VA系统列表 GET /vas/list
@api_bp.route('/vas/list', methods=['GET'])
def get_va_systems():
    """获取所有VA系统列表"""
    try:
        # 读取va_states目录下的所有JSON文件
        systems = []
        for state_file in VA_STATES_DIR.glob("*.json"):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    va_id = state.get("id", state_file.stem)
                    systems.append({
                        "id": va_id,
                        "name": state.get("name", f"My Visual Analytics System"),
                        "created": state.get("created", int(time.time()))
                    })
            except:
                continue

        return format_response(200, "获取系统列表成功", systems)

    except Exception as e:
        return format_response(500, f"获取系统列表失败: {str(e)}")


# 6. 获取VA系统详情 GET /vas
@api_bp.route('/vas', methods=['GET'])
def get_va_system():
    """获取指定VA系统详情"""
    try:
        va_id = request.args.get('id')
        if not va_id:
            return format_response(400, "缺少系统ID")

        va_info = load_state(va_id)
        if not va_info:
            return format_response(404, "未找到VA系统")

        return format_response(200, "获取系统详情成功", va_info)

    except Exception as e:
        return format_response(500, f"获取系统详情失败: {str(e)}")


# 7. 创建新VA系统 POST /vas
@api_bp.route('/vas', methods=['POST'])
def create_va_system():
    """创建新的VA系统 - 无需请求参数"""
    try:
        # 生成ID
        va_id = f"va_{int(time.time())}"
        # 创建系统基本信息
        va_info = {
            "id": va_id,
            "name": f"Visual Analytics System {va_id}",
            "created": int(time.time())
        }
        save_state(va_id, va_info)
        # 返回创建的系统信息
        return format_response(200, "创建系统成功", {
            "id": va_id,
            "name": va_info["name"]
        })
    except Exception as e:
        return format_response(500, f"创建系统失败: {str(e)}")


# 8. 删除VA系统 DELETE /vas
@api_bp.route('/vas', methods=['DELETE'])
def delete_va_system():
    """删除指定VA系统"""
    try:
        va_id = request.args.get('id')
        if not va_id:
            return format_response(400, "缺少系统ID")

        # 删除数据库
        db_path = DATABASES_DIR / f"{va_id}.db"
        if db_path.exists():
            os.remove(db_path)

        # 删除VA状态
        state_path = _state_path(va_id)
        if state_path.exists():
            os.remove(state_path)

        # 删除结果
        result_dir = Path(f'result/{va_id}')
        if result_dir.exists() and result_dir.is_dir():
            import shutil
            shutil.rmtree(result_dir)

        # 删除中间表
        for csv_file in TABLES_DIR.glob(f"{va_id}_*.csv"):
            os.remove(csv_file)

        return format_response(200, "删除系统成功", None)

    except Exception as e:
        return format_response(500, f"删除系统失败: {str(e)}")