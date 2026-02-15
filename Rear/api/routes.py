from flask import Blueprint, request, jsonify, send_file, stream_with_context, Response
import sqlite3
import os
from pathlib import Path
import json
import time
import traceback
from modules.agent import NewExplorationThread
from utils.sql import csv_to_sqlite

sqlite3.threadsafety = 1

api_bp = Blueprint('api', __name__)

BASE_DIR = Path(__file__).parent.parent
DATABASES_DIR = BASE_DIR / "databases"
TABLES_DIR = BASE_DIR / "tables"
VA_STATES_DIR = Path(__file__).parent / "va_states"

for dir_path in [DATABASES_DIR, TABLES_DIR, VA_STATES_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)


def format_response(code=200, message="", data=None):
    """Generate standardized JSON response"""
    return jsonify({
        "code": code,
        "message": message,
        "data": data if data is not None else []
    })


def _state_path(va_id: str) -> Path:
    """Get the path to the VA system state file"""
    return VA_STATES_DIR / f"{va_id}.json"


def save_state(va_id: str, state: dict):
    """Save VA system state to va_states directory"""
    state_path = _state_path(va_id)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_state(va_id: str) -> dict:
    """Load VA system state from va_states directory"""
    path = _state_path(va_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# 1. Upload database POST /database
@api_bp.route('/database', methods=['POST'])
def upload_database():
    """Process database file upload and parse table structure"""
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

        # Save database
        db_path = DATABASES_DIR / f"{va_id}.db"
        file.save(str(db_path))

        if file.filename.endswith('.zip'):
            import zipfile
            csv_dir = DATABASES_DIR / f"{va_id}_csv"
            csv_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(str(db_path), 'r') as zip_ref:
                zip_ref.extractall(csv_dir)

            csv_to_sqlite(str(csv_dir), str(db_path))

            # Clean up temporary directory
            import shutil
            shutil.rmtree(csv_dir)

        try:
            # Initialize database analysis using NewExplorationThread
            exploration = NewExplorationThread(
                db_path=str(db_path),
                desc="",
                goal="",
                result_id=va_id,
                use_reflect=False,
                use_rag=False,
                models={}
            )

            # Execute database understanding step
            exploration.current_stage_id = 0
            exploration._step()
            dataset = exploration.dataset
        except Exception as e:
            print(f"Database processing error: {str(e)}, using fallback method")

            # Fallback: Direct database processing
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
                        'description': f"Field {column[1]}, type {column[2]}"
                    }
                    table_info['columns'].append(col_info)

                database_info.append(table_info)

            dataset = {
                'tables': database_info,
                'description': f"Database contains the following tables: {', '.join([t[0] for t in tables])}"
            }

            conn.close()

            with open(f'result/{va_id}/0.txt', 'w', encoding='utf-8') as f:
                json.dump(dataset, f, ensure_ascii=False)

        # Save VA system basic information
        va_info = {
            "id": va_id,
            "name": f"Visual Analytics System {va_id}",
            "created": int(time.time()),
            "dataset": dataset
        }
        save_state(va_id, va_info)

        # Build response
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


# 2. Generate results POST /generate
@api_bp.route('/generate', methods=['POST'])
def generate_results():
    """Generate VA system content for each stage and stream results"""
    try:
        data = request.json
        if not data:
            return format_response(400, "Invalid request content")
        va_id = data.get("id")
        if not va_id:
            return format_response(400, "Missing system ID")

        os.makedirs(f'result/{va_id}', exist_ok=True)

        # Load VA system information
        va_info = load_state(va_id)
        if not va_info:
            return format_response(404, "VA system not found")
        db_path = DATABASES_DIR / f"{va_id}.db"
        if not db_path.exists():
            return format_response(404, f"Database file not found: {va_id}.db")
        # Get request parameters
        desc = data.get("desc", "")
        goal = data.get("goal", "")
        initial_stage = data.get("initialStage", 0)
        max_steps = data.get("maxSteps", 10)
        use_reflect = data.get("useReflect", True)
        use_rag = data.get("useRag", False)

        # Set model configuration
        models = data.get("models", {
            "database": "gpt-4o",
            "requirements": "gpt-4o",
            "tasks": "gpt-4o",
            "plan": "gpt-4o",
            "sql": "gpt-4o",
            "vega": "gpt-4o"
        })

        # Create new exploration thread
        exploration = NewExplorationThread(
            db_path=str(db_path),
            desc=desc,
            goal=goal,
            result_id=va_id,
            max_steps=max_steps,
            use_reflect=use_reflect,
            use_rag=use_rag,
            models=models
        )

        # Set initial stage and data
        if initial_stage > 0:
            exploration.current_stage_id = initial_stage
            if "dataset" in data:
                exploration.dataset = data["dataset"]
            else:
                exploration.dataset = va_info.get("dataset", {})
            if initial_stage > 1 and "requirements" in data:
                exploration.outputs["requirements"] = data["requirements"]
            if initial_stage > 2 and "tasks" in data:
                exploration.outputs["tasks"] = data["tasks"]
            if initial_stage > 3 and "plan" in data:
                exploration.outputs["views"] = data["plan"].get("views", [])
                exploration.outputs["graph"] = data["plan"].get("graph", [])
                exploration.outputs["path"] = data["plan"].get("path", "")
            if initial_stage > 4 and "sqls" in data:
                exploration.outputs["sqls"] = data["sqls"]
            if initial_stage > 5 and "vlcodes" in data:
                exploration.outputs["vlcodes"] = data["vlcodes"]

        # Create streaming response
        def generate():
            # Use a step counter for response ordering
            response_step = 0
            # Timeout mechanism
            start_time = time.time()
            max_duration = 300
            while (exploration.current_steps < exploration.max_steps and
                   exploration.current_stage_id < len(exploration.stages) and
                   time.time() - start_time < max_duration):
                # Record state before current step
                prev_stage = exploration.current_stage_id
                prev_steps = exploration.current_steps
                if prev_stage >= len(exploration.stages):
                    print(f"All stages completed (stage_id: {prev_stage}), ending execution")
                    break
                # Execute current step
                print(f"Executing step: {prev_steps}, stage: {exploration.stages[prev_stage]}")
                exploration._step()
                print(f"Step completed: {prev_steps}, new stage: {exploration.current_stage_id}")

                # Prepare output for current step
                current_output = {
                    "stage": exploration.stages[prev_stage],
                    "stageId": prev_stage,
                    "outputs": {}
                }

                # Add appropriate outputs based on current stage
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
                    print(f"Generating VEGA-LITE, current step: {prev_steps}")
                    current_output["outputs"]["vlcodes"] = exploration.outputs.get("vlcodes", {})
                    vega_size = len(str(exploration.outputs.get("vlcodes", {})))
                    print(f"VEGA-LITE generation complete, vlcodes size: {vega_size} characters")

                output_file = Path(f'result/{va_id}/{prev_steps}.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(current_output, f, ensure_ascii=False)

                try:
                    raw_content = output_file.read_text(encoding="utf-8") if output_file.exists() else ""
                except Exception as e:
                    print(f"Failed to read step output: {str(e)}")
                    raw_content = ""

                response_data = {
                    "step": response_step,
                    "raw": raw_content
                }
                response_step += 1

                yield json.dumps(response_data, ensure_ascii=False) + "\n"

            if "vlcodes" in exploration.outputs and (exploration.current_stage_id == 6):
                print("Sending final Vega-Lite confirmation")
                final_output = {
                    "stage": "VEGA-LITE GENERATION",
                    "stageId": 5,
                    "outputs": {
                        "vlcodes": exploration.outputs["vlcodes"]
                    }
                }
                final_file = Path(f'result/{va_id}/complete.txt')
                with open(final_file, 'w', encoding='utf-8') as f:
                    json.dump(final_output, f, ensure_ascii=False)

                try:
                    final_content = final_file.read_text(encoding="utf-8") if final_file.exists() else ""
                except Exception as e:
                    print(f"Failed to read final output: {str(e)}")
                    final_content = ""

                final_response = {
                    "step": response_step,
                    "raw": final_content,
                    "finish": "COMPLETE"
                }
                yield json.dumps(final_response, ensure_ascii=False) + "\n"

            # Update and save final VA state
            va_info.update({
                "desc": desc,
                "goal": goal,
                "dataset": exploration.dataset,
                "evaluation_result": exploration.evaluation_result
            })

            # Save results for each stage
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

            save_state(va_id, va_info)
            print(f"Process complete, sent results for {response_step} steps")

        return Response(stream_with_context(generate()), mimetype='application/json')

    except Exception as e:
        print(traceback.format_exc())
        return format_response(500, f"Error in generation process: {str(e)}")


# 3. Save modified results POST /save
@api_bp.route('/save', methods=['POST'])
def save_results():
    """Save modified VA system information"""
    try:
        data = request.json
        if not data:
            return format_response(400, "Invalid request content")
        va_id = data.get("id")
        if not va_id:
            return format_response(400, "Missing system ID")
        va_info = load_state(va_id)
        if not va_info:
            return format_response(404, "VA system not found")

        # Update submitted fields
        for key in data:
            if key != "id":  # Don't update ID
                va_info[key] = data[key]

        save_state(va_id, va_info)

        return format_response(200, "Saved", None)

    except Exception as e:
        return format_response(500, f"Save failed: {str(e)}")


# 4. Get CSV file GET /
@api_bp.route('/', methods=['GET'])
def get_csv_file():
    """Return specified CSV file"""
    try:
        name = request.args.get('name')
        if not name or not name.endswith('.csv'):
            return format_response(400, "Invalid filename")

        file_path = TABLES_DIR / name
        if not file_path.exists():
            return format_response(404, "File not found")

        return send_file(str(file_path))

    except Exception as e:
        return format_response(500, f"Failed to get file: {str(e)}")


# 5. Get VA system list GET /vas/list
@api_bp.route('/vas/list', methods=['GET'])
def get_va_systems():
    """Get list of all VA systems"""
    try:
        # Read all JSON files from va_states directory
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

        return format_response(200, "Successfully retrieved system list", systems)

    except Exception as e:
        return format_response(500, f"Failed to get system list: {str(e)}")


# 6. Get VA system details GET /vas
@api_bp.route('/vas', methods=['GET'])
def get_va_system():
    """Get details for specified VA system"""
    try:
        va_id = request.args.get('id')
        if not va_id:
            return format_response(400, "Missing system ID")

        va_info = load_state(va_id)
        if not va_info:
            return format_response(404, "VA system not found")

        return format_response(200, "Successfully retrieved system details", va_info)

    except Exception as e:
        return format_response(500, f"Failed to get system details: {str(e)}")


# 7. Create new VA system POST /vas
@api_bp.route('/vas', methods=['POST'])
def create_va_system():
    """Create new VA system - no request parameters needed"""
    try:
        va_id = f"va_{int(time.time())}"
        va_info = {
            "id": va_id,
            "name": f"Visual Analytics System {va_id}",
            "created": int(time.time())
        }
        save_state(va_id, va_info)
        return format_response(200, "System created successfully", {
            "id": va_id,
            "name": va_info["name"]
        })
    except Exception as e:
        return format_response(500, f"Failed to create system: {str(e)}")


# 8. Delete VA system DELETE /vas
@api_bp.route('/vas', methods=['DELETE'])
def delete_va_system():
    """Delete specified VA system"""
    try:
        va_id = request.args.get('id')
        if not va_id:
            return format_response(400, "Missing system ID")
        db_path = DATABASES_DIR / f"{va_id}.db"
        if db_path.exists():
            os.remove(db_path)
        state_path = _state_path(va_id)
        if state_path.exists():
            os.remove(state_path)
        result_dir = Path(f'result/{va_id}')
        if result_dir.exists() and result_dir.is_dir():
            import shutil
            shutil.rmtree(result_dir)
        for csv_file in TABLES_DIR.glob(f"{va_id}_*.csv"):
            os.remove(csv_file)

        return format_response(200, "System deleted successfully", None)

    except Exception as e:
        return format_response(500, f"Failed to delete system: {str(e)}")