from utils.model import get_model_response
import json
from update import update
from schema import Schema, And, Or, Use, Optional, SchemaError

def generate_sql(user_goal: str, database_info: dict, plan: dict, model: str = 'openai') -> dict:
    messages = [
        {
            'role': 'system',
            'content': open('prompts/sql_generation.txt', 'r').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False)).replace('<USER GOAL HERE>', user_goal)
        },
        {
            'role': 'user',
            'content': 'The user\'s plan for the VAS is as follows: \n\n' + json.dumps(plan, ensure_ascii = False)
        },
    ]
    result = get_model_response(messages, model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()
    result_schema = Schema({
        "sqls": [
        {
            "id": Or(And(int, lambda x:x>0), And(str, lambda x:int(x)>0)),
            "name": And(str),
            "SQL": And(str),
            "corrView": Or(And(int, lambda x:x>0), And(str, lambda x:int(x)>0)),
            "pk": And(str),
            "fk": [
                {
                    "key": And(str),
                    "table": And(str),
                }
            ]
        }
    ]
    })
    update(messages, result, result_schema)
    return json.loads(result)


def regenerate_sql(user_goal: str, database_info: dict, plan: dict, original_sql: dict, exception: str, model: str = 'openai') -> dict:
    result = get_model_response([
        {
            'role': 'system',
            'content': open('prompts/regenerate_sql.txt', 'r').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False)).replace('<USER GOAL HERE>', user_goal)
        },
        {
            'role': 'user',
            'content': 'The user\'s plan for the VAS is as follows: \n\n' + json.dumps(plan, ensure_ascii = False) + 'The original SQL queries are as follows: \n\n' + json.dumps(original_sql, ensure_ascii = False) + '\n\nThe exception that user encountered is as follows: \n\n' + exception
        }
    ], model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()
    
    return json.loads(result)