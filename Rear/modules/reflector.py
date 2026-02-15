import json
from utils.model import get_model_response
import base64


def reflect(user_goal: str, database_info: dict, outputs: dict, sql_error_msg: str = '', vega_lite_error_msg: str = '', stage: str = 'DESIGN REQUIREMENTS', model: str = 'openai') -> dict:
    messages = [
        {
            'role': 'system',
            'content': open('prompts/reflect.txt', 'r', encoding = 'utf-8').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False)).replace('<USER GOAL HERE>', user_goal).replace('<CURRENT STAGE HERE>', stage)
        },
        {
            'role': 'user',
            'content': 'The user determined the following design requirements:\n\n' + json.dumps(outputs['requirements'], ensure_ascii = False, indent = 4)
        },
    ]
    if outputs.get('tasks'):
        messages.append({
            'role': 'user',
            'content': 'The user determined the following analytical tasks:\n\n' + json.dumps(outputs['tasks'], ensure_ascii = False)
        })
    if outputs.get('plan'):
        messages.append({
            'role': 'user',
            'content': 'The user designed the following analysis plan for the VAS:\n\n' + json.dumps(outputs['plan'], ensure_ascii = False)
        })
    if outputs.get('sql'):
        messages.append({
            'role': 'user',
            'content': 'The user used the following SQL statements to create intermediate tables:\n\n' + json.dumps(outputs['sql'], ensure_ascii = False)
        })
    if sql_error_msg:
        messages.append({
            'role': 'user',
            'content': 'The user encountered the following erros when generating SQL: ' + sql_error_msg
        })
    if outputs.get('vlcodes'):
        messages.append({
            'role': 'user',
            'content': 'The user wrote the following Vega-Lite code:\n\n' + json.dumps(outputs['vlcodes'], ensure_ascii = False)
        })
    if vega_lite_error_msg:
        messages.append({
            'role': 'user',
            'content': 'The user encountered the following errors in Vega-Lite code:\n\n' + vega_lite_error_msg
        })
    
    result = get_model_response(messages, model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()
    
    return json.loads(result)


def reflect_all(user_goal: str, database_info: dict, requirements: dict, tasks: dict, plan: dict, sql: dict, vega_lite: str, image_path: str = '', error_msg: str = '') -> str:
    with open(image_path, 'rb') as file:
        image_base64 = base64.b64encode(file.read()).decode()
    result = get_model_response([
        {
            'role': 'system',
            'content': open('prompts/reflect.txt', 'r').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False)).replace('<USER GOAL HERE>', user_goal)
        },
        {
            'role': 'user',
            'content': 'The user\'s design requirements are as follows:\n\n' + json.dumps(requirements, ensure_ascii = False)
        },
        {
            'role': 'user',
            'content': 'The user specified the following analytical tasks:\n\n' + json.dumps(tasks, ensure_ascii = False)
        },
        {
            'role': 'user',
            'content': 'The user generated the following intermediate tables:\n\n' + json.dumps(sql, ensure_ascii = False)
        },
        {
            'role': 'user',
            'content': 'The user\'s plan is as follows:\n\n' + json.dumps(plan, ensure_ascii = False)
        },
        {
            'role': 'user',
            'content': 'The user wrote the following Vega-Lite code:\n\n' + vega_lite
        },
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'The final effect of the above Vega-Lite is as follows:'},
                {'type': 'image', 'source': {
                    'type': 'base64',
                    'media_type': 'image/png',
                    'data': image_base64
                }}
            ]
        } if image_path != '' else {
            'role': 'user',
            'content': 'The user encountered the following errors in Vega-Lite code:\n\n' + error_msg
        }
    ])

    return result