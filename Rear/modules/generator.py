from utils.model import get_model_response
import json
from update import update
from schema import Schema, And, Or, Use, Optional, SchemaError

def generate_vega(user_goal: str, database_info: dict, plan: dict, sql: dict, model: str = 'openai') -> json:
    messages = [
        {
            'role': 'system',
            'content': open('prompts/vega_generation.txt', 'r').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False)).replace('<USER GOAL HERE>', user_goal).replace('<INTERMEDIATE TABLES HERE>', json.dumps(sql, ensure_ascii = False, indent = 4))
        },
        {
            'role': 'user',
            'content': 'The user\'s design for each view is as follows: \n\n' + json.dumps(plan, ensure_ascii = False, indent = 4)
        }
    ]
    result = get_model_response(messages, model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()
    result_schema = Schema({str: object})
    update(messages, result, result_schema)
    return {'vlcodes': json.loads(result)}

def regenerate_vega(user_goal: str, database_info: dict, plan: dict, sql: dict, original_vega: dict, exception: str, model: str = 'openai') -> json:
    result = get_model_response([
        {
            'role': 'system',
            'content': open('prompts/vega_regeneration.txt', 'r').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False)).replace('<USER GOAL HERE>', user_goal).replace('<INTERMEDIATE TABLES HERE>', json.dumps(sql, ensure_ascii = False, indent = 4))
        },
        {
            'role': 'user',
            'content': 'The user\'s design for each view is as follows: \n\n' + json.dumps(plan, ensure_ascii = False, indent = 4) + '\n\nThe original Vega-Lite code is as follows: \n\n' + json.dumps(original_vega, ensure_ascii = False, indent = 4) + '\n\nThe exception that user encountered is as follows: \n\n' + exception
        }
    ], model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()

    return {'vlcodes': json.loads(result)}