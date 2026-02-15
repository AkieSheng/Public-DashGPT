from utils.model import get_model_response
from utils.sql import get_intermediate_table
import sqlite3
import math
import pandas as pd
import json
import altair as alt
from schema import Schema
from typing import Tuple
from time import sleep
import traceback

from modules.understander import understand_database
from modules.decomposer import decompose_goals, generate_tasks
from modules.planner import plan
from modules.sqlgenerator import generate_sql, regenerate_sql
from modules.generator import generate_vega, regenerate_vega
from modules.reflector import reflect


class NewExplorationThread:
    def __init__(self, db_path: str, desc: str, goal: str, result_id='default', model: str = "gpt-4o",
                 models: dict = None, max_steps: int = 10, use_reflect: bool = True,
                 use_rag: bool = False):
        self.db_path = db_path
        self.goal = goal
        self.desc = desc
        self.default_model = model
        self.models = models
        self.max_steps = max_steps
        self.current_steps = 0
        self.result_id = result_id
        self.use_rag = use_rag
        self.evaluation_result = {
            'failed_format_following': 0,
            'total_sql': 0,
            'total_error_sql': 0,
            'total_vl': 0,
            'total_error_vl': 0,
            'total_steps': 0
        }

        self.stages = [
            'DATABASE UNDERSTANDING',
            'REQUIREMENT GENERATION',
            'TASK GENERATION',
            'PLAN GENERATION',
            'SQL GENERATION',
            'VEGA-LITE GENERATION'
        ]
        self.current_stage_id = 0

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.outputs = dict()

        self.stage_attempts = {i: 0 for i in range(len(self.stages))}
        self.max_attempts_per_stage = 5

    def _get_stage_model(self, stage_id):
        stage_to_key = {
            0: "database", 1: "requirements", 2: "tasks",
            3: "plan", 4: "sql", 5: "vega"
        }
        key = stage_to_key.get(stage_id)
        if not self.models:
            return self.default_model
        if key and key in self.models:
            return self.models[key]
        if "default" in self.models:
            return self.models["default"]
        return self.default_model

    def _validate_vega_lite(self) -> str | None:
        return None
        try:
            chart = alt.Chart().from_dict(self.outputs['vlcodes'])
            chart.save('vis.png')
        except Exception as e:
            self.evaluation_result['total_error_vl'] += 1
            print(e)
            return str(e)
        return None

    def explore(self) -> dict:
        while self._step() and self.current_steps < self.max_steps and self.current_stage_id < len(self.stages):
            pass
        self.evaluation_result['total_steps'] = self.current_steps
        return self.evaluation_result

    def _update_outputs(self, obj: dict):
        self.outputs.update(obj)

    def _step(self) -> bool:
        print(self.current_steps, self.stages[self.current_stage_id])
        try:
            if self.current_stage_id == 0:
                model = self._get_stage_model(0)
                self.dataset = understand_database(self.cursor, self.conn, self.desc, model = model)
                self.dataset['description'] = self.desc
                self.current_stage_id += 1
            elif self.current_stage_id == 1:
                model = self._get_stage_model(1)
                self._update_outputs(decompose_goals(self.goal, self.dataset, model = model, use_rag = self.use_rag))
                self.current_stage_id += 1
            elif self.current_stage_id == 2:
                model = self._get_stage_model(2)
                self._update_outputs(generate_tasks(self.goal, self.desc, self.dataset, self.outputs['requirements'], model = model, use_rag = self.use_rag))
                self.current_stage_id += 1
            elif self.current_stage_id == 3:
                model = self._get_stage_model(3)
                self._update_outputs(plan(self.goal, self.desc, self.dataset, self.outputs['tasks'], model = model))
                self.current_stage_id += 1
            elif self.current_stage_id == 4:
                model = self._get_stage_model(4)
                self.evaluation_result['total_sql'] += 1
                if self.outputs.get('sql_err_msg'):
                    self._update_outputs(regenerate_sql(self.goal, self.dataset, self.outputs['views'], self.outputs['sqls'], self.outputs['sql_err_msg'], model = model))
                    del self.outputs['sql_err_msg']
                else:
                    self._update_outputs(generate_sql(self.goal, self.dataset, self.outputs['views'], model = model))
                try:
                    for table in self.outputs['sqls']:
                        get_intermediate_table(self.cursor, self.conn, table['SQL'], table['name'])
                    self.outputs['sql_err_msg'] = None
                    self.current_stage_id += 1
                except Exception as e:
                    print(e)
                    self.evaluation_result['total_error_sql'] += 1
                    self.outputs['sql_err_msg'] = str(e)
            elif self.current_stage_id == 5:
                model = self._get_stage_model(5)
                self.evaluation_result['total_vl'] += 1
                if self.outputs.get('vl_err_msg'):
                    self._update_outputs(regenerate_vega(self.goal, self.dataset, self.outputs['views'], self.outputs['sqls'], self.outputs['vlcodes'], self.outputs['vl_err_msg'], model = model))
                    del self.outputs['vl_err_msg']
                else:
                    self._update_outputs(generate_vega(self.goal, self.dataset, self.outputs['views'], self.outputs['sqls'], model = model))
                self.outputs['vl_err_msg'] = self._validate_vega_lite()
                if not self.outputs['vl_err_msg']:
                    self.current_stage_id += 1
            else:
                return False
        except Exception as e:
            print('Error in step:', e)
            print(traceback.format_exc())
        finally:
            self.current_steps += 1

        return True

    def __del__(self):
        self.conn.close()


class ExplorationThread:
    # init method or constructor
    def __init__(self, db_path: str, desc: str, goal: str, result_id='default', model: str = 'gpt-4o',
                 max_steps: int = 20, use_reflect=False):
        self.db_path = db_path
        self.goal = goal
        self.desc = desc
        self.model = model
        self.max_steps = max_steps
        self.current_steps = 0
        self.feedback = None
        self.result_id = result_id
        self.evaluation_result = {
            'failed_format_following': 0,
            'total_sql': 0,
            'total_error_sql': 0,
            'total_vl': 0,
            'total_error_vl': 0,
            'total_steps': 0
        }

        self.stages = [
            'DATABASE UNDERSTANDING',
            'REQUIREMENT GENERATION',
            'TASK GENERATION',
            'PLAN GENERATION',
            'SQL GENERATION',
            'VEGA-LITE GENERATION',
            'FINAL REVIEW'
        ]
        self.current_stage_id = 0

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.outputs = dict()

    def explore(self) -> dict:
        while not self._step():
            pass
        self.evaluation_result['total_steps'] += self.current_steps
        return self.evaluation_result

    def _step(self) -> bool:
        print(self.current_steps, self.current_stage_id)
        if self.current_stage_id == 0:
            try:
                self.dataset = self._understand_database()
                # If OK, go to next stage
                self.current_stage_id = 1
                with open(f'result/{self.result_id}/{self.current_steps}.txt', 'w', encoding='utf-8') as file:
                    file.write(json.dumps(self.dataset))
            except Exception as e:
                print(str(e))
                pass
        else:
            response = self._compose_content()
            with open(f'result/{self.result_id}/{self.current_steps}.txt', 'w', encoding='utf-8') as file:
                file.write(response)

            if self.current_stage_id == 4:  # SQL Generation
                self.evaluation_result['total_sql'] += 1
            if self.current_stage_id == 5:
                self.evaluation_result['total_vl'] += 1

            try:
                _, answer = self._get_response_content(response)
                if answer.get('go_ahead'):
                    self.outputs.update(answer)
                    if self.current_stage_id == 4:  # SQL Generation
                        try:
                            for table in answer['sqls']:
                                get_intermediate_table(self.cursor, self.conn, table['SQL'], table['name'])
                            self.current_stage_id += 1
                        except Exception as e:
                            self.evaluation_result['total_error_sql'] += 1
                            self.outputs['sql_err_msg'] = str(e)
                            print(str(e))
                    else:
                        self.current_stage_id += 1
                else:
                    self.current_stage_id = answer['stageId']
                    self.feedback = answer['feedback']
                    print(self.feedback)
            except Exception as e:
                print('Invalid format:', e)
                self.current_steps += 1
                self.evaluation_result['failed_format_following'] += 1
                return self._check_end()

        self.current_steps += 1
        return self._check_end()

    def _understand_database(self) -> dict:
        try:
            database_info = []
            self.cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
            tables = self.cursor.fetchall()
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f'PRAGMA table_info({table_name})')
                columns = self.cursor.fetchall()

                df = pd.read_sql_query(f'SELECT * FROM {table_name}', self.conn)
                # check if dataframe is empty
                if df.empty:
                    stats = {}
                    for column in columns:
                        stats[column[1]] = {'count': 0, 'samples': []}
                else:
                    # Get statistics
                    try:
                        stats = df.describe(include='all').to_dict()
                    except Exception as e:
                        print(f"Error calculating statistics: {str(e)}")
                        stats = {}
                        for column in columns:
                            stats[column[1]] = {'count': len(df), 'samples': []}
                # Add sample values for each column
                table_columns = []
                for column in columns:
                    column_name = column[1]
                    column_stats = {}
                    # Get statistics for this column
                    if column_name in stats:
                        column_stats = {
                            key: value for key, value in stats[column_name].items()
                            if type(value) != float or not math.isnan(value)
                        }
                    # Get sample values
                    samples = []
                    try:
                        if not df.empty and column_name in df.columns:
                            samples = list(df[column_name].value_counts().to_dict().keys())[:5]
                    except Exception as e:
                        print(f"Error getting samples for column {column_name}: {str(e)}")
                    column_info = {
                        'column': column_name,
                        'dtype': column[2],
                        'stats': column_stats
                    }
                    if samples:
                        column_info['stats']['samples'] = samples
                    table_columns.append(column_info)

                database_info.append({
                    'table': table_name,
                    'columns': table_columns
                })
            # Generate description using LLM
            try:
                result = get_model_response([
                    {
                        'role': 'system',
                        'content': open('prompts/database_understanding.txt', 'r').read()
                    },
                    {
                        'role': 'user',
                        'content': json.dumps({
                            'userDescription': self.desc,
                            'databaseInfo': database_info
                        }, ensure_ascii=False)
                    }
                ], model=self.model)
                print("LLM Result:", result)
                # Parse LLM response
                if result.strip().startswith('```json'):
                    result = result.strip()[8:-3].strip()
                parsed_result = json.loads(result)
                # Validate parsed result
                if 'description' in parsed_result and 'tables' in parsed_result:
                    # Update database information
                    final_database_info = {
                        'tables': database_info,
                        'description': parsed_result['description']
                    }
                    # Add column descriptions
                    for i in range(len(parsed_result['tables'])):
                        if i < len(final_database_info['tables']):
                            for j in range(len(parsed_result['tables'][i]['columns'])):
                                if j < len(final_database_info['tables'][i]['columns']):
                                    final_database_info['tables'][i]['columns'][j]['description'] = \
                                        parsed_result['tables'][i]['columns'][j]['description']
                    return final_database_info
                else:
                    raise ValueError("LLM response missing required fields")
            except Exception as e:
                print(f"LLM processing error: {str(e)}")
                # If LLM processing fails, return basic database info
                return {
                    'tables': database_info,
                    'description': f"Database with {len(database_info)} tables: {', '.join([table['table'] for table in database_info])}"
                }
        except Exception as e:
            print(f"Database parsing error: {str(e)}")
            # On any error, call fallback method
            return self._create_fallback_dataset()

    def _create_fallback_dataset(self) -> dict:
        """Create a basic dataset structure when database understanding stage fails"""
        database_info = []
        try:
            # Get basic structure directly from database
            self.cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
            tables = self.cursor.fetchall()
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f'PRAGMA table_info({table_name})')
                columns = self.cursor.fetchall()

                table_columns = []
                for column in columns:
                    column_info = {
                        'column': column[1],
                        'dtype': column[2],
                        'description': f"Column {column[1]} with type {column[2]}"  # Simple description
                    }
                    table_columns.append(column_info)
                database_info.append({
                    'table': table_name,
                    'columns': table_columns
                })

            # Add some sample data
            for table_info in database_info:
                table_name = table_info['table']
                try:
                    # Get first 5 rows from each table as samples
                    df = pd.read_sql_query(f'SELECT * FROM {table_name} LIMIT 5', self.conn)
                    for column in table_info['columns']:
                        column_name = column['column']
                        if column_name in df.columns:
                            column['samples'] = df[column_name].tolist()
                except Exception as e:
                    print(f"Error getting sample data for table {table_name}: {str(e)}")
        except Exception as e:
            print(f"Error creating fallback dataset: {str(e)}")
            # If still fails, create a minimal structure
            return {
                'tables': [],
                'description': "Database structure could not be determined."
            }
        return {
            'tables': database_info,
            'description': f"Database with {len(database_info)} tables: {', '.join([table['table'] for table in database_info])}"
        }
        
    def _validate_vega_lite(self) -> str | None:
        if not self.outputs.get('vlcodes'):
            return None
        try:
            chart = alt.Chart().from_dict(self.outputs['vlcodes'])
            chart.save('vis.svg')
        except Exception as e:
            self.evaluation_result['total_error_vl'] += 1
            return str(e)
        return None

    def _compose_content(self) -> str:
        input = {
            'goal': self.goal,
            'dataset': self.dataset,
            'stageName': self.stages[self.current_stage_id],
            'stageId': self.current_stage_id
        }
        if self.current_stage_id >= 2:
            input.update({
                'requirements': self.outputs['requirements']
            })
        if self.current_stage_id >= 3:
            input.update({
                'tasks': self.outputs['tasks']
            })
        if self.current_stage_id >= 4:
            input.update({
                'views': self.outputs['views'],
                'graph': self.outputs['graph'],
                'path': self.outputs['path']
            })
            if self.outputs.get('sqls') and self.outputs.get('sql_err_msg'):
                input.update({
                    'previousSqls': self.outputs['sqls']
                })
        if self.current_stage_id >= 5:
            input.update({
                'sqls': self.outputs['sqls']
            })
            if self.outputs.get('vlcodes'):
                input.update({
                    'previousVlcodes': self.outputs['vlcodes']
                })
        if self.outputs.get('sql_err_msg'):
            input.update({
                'sqlErrMsg': self.outputs['sql_err_msg']
            })
            del self.outputs['sql_err_msg']
        if self.current_stage_id >= 6:
            input.update(self._validate_vega_lite())
        if self.feedback:
            input.update({
                'feedback': self.feedback
            })
            self.feedback = None

        print(list(map(lambda x: x[0], input.items())))

        retries = 0
        while True:
            try:
                response = get_model_response([
                    {
                        'role': 'system',
                        'content': open('prompts/0_prompts_one.txt', 'r', encoding = 'utf-8').read()
                    },
                    {
                        'role': 'user',
                        'content': json.dumps(input, ensure_ascii = False)
                    },
                    {
                        'role': 'user',
                        'content': 'If the Assistant believes that there are no problem with previous results, the output should be in the following JSON format:\n' + open(f'prompts/output_format/{self.current_stage_id}.txt', encoding = 'utf-8').read() + 
                        '''
                        However, if any problem exists in PREVIOUS stages (not current stage) and the Assistant decides to trace back, the output JSON format should be: 
                        {
                            "think": "...", // The reasoning process
                            "go_ahead": false,
                            "feedback": "..."
                            "stageName": "REQUIREMENT GENERATION" | "TASK GENERATION" | "PLAN GENERATION" | "SQL GENERATION" | "VEGA-LITE GENERATION" | "FINAL REVIEW",
                            "stageId": ... // The index of the stage to go. Must be a number (strictly) less than current stage ID
                        }'''
                    }
                ])
                break
            except Exception as e:
                retries += 1
                print(e)
                print(f'Failed to get model response, retrying ({retries})...')
                sleep(3)

        return response

    def _validate_schema(self, obj: dict):
        sc = {
            1: {
                'go_ahead': bool,
                'requirements': list
            },
            2: {
                'go_ahead': bool,
                'tasks': list
            },
            3: {
                'go_ahead': bool,
                'views': list,
                'graph': list,
                'path': str
            },
            4: {
                'go_ahead': bool,
                'sqls': list
            },
            5: {
                'go_ahead': bool,
                'vlcodes': dict
            }
        }[self.current_stage_id]
        Schema(sc).validate(obj)

    # check whether the format of outputs is valid
    def _get_response_content(self, content: str) -> Tuple[str, dict]:
        if content.strip().startswith('```json'):
            content = content.strip()[8:-3].strip()

        obj = json.loads(content)
        think_content = obj['think']
        del obj['think']

        if obj['go_ahead']:
            self._validate_schema(obj)

        return think_content, obj

    # check whether the exploration should be ended
    def _check_end(self) -> bool:
        if self.current_steps >= self.max_steps or self.current_stage_id >= 7:
            return True
        else:
            return False
    
    def __del__(self):
        self.conn.close()
