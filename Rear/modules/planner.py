from utils.model import get_model_response
import json
from update import update
from schema import Schema, And, Or, Use, Optional, SchemaError

def plan(user_goal: str, database_info: str, design_requirements: dict, tasks: dict, model: str = 'openai') -> dict:
    messages = [
        {
            'role': 'system',
            'content': open('prompts/plan.txt', 'r', encoding = 'utf-8').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False)).replace('<USER GOAL HERE>', user_goal)
        },
        {
            'role': 'user',
            'content': 'The user wrote the following design requirements for the VAS:\n\n' + json.dumps(design_requirements, ensure_ascii = False)
        },
        {
            'role': 'user',
            'content': 'The user specified the following analytical tasks:\n\n' + json.dumps(tasks, ensure_ascii = False)
        }
    ]

    result = get_model_response(messages, model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()
    result_schema = Schema({
        "views": [
        {
            "id": Or(And(int, lambda x:x>0), And(str, lambda x:int(x)>0)),
            "level": Or("overview","exploration","detail","insight"),
            "fields": [
                And(str),
            ],
            "task": [Or(And(int, lambda x:x>0), And(str, lambda x:int(x)>0))], 
            "visualization": {
                "markType": And(str),
                "encodings": [
                    And(str),
                ],
                "description": And(str),
            }, 
            "usingParams": [ 
                And(str)
            ], 
            Optional('components'):any,
            "interactions": [
                {
                    "object": And(str),
                    "verb": And(str),
                    "effect": {
                        "description": And(str),
                        "params": [{
                            "name": And(str),
                            "select": {
                                "type": Or("point","interval"),
                                "encodings": [
                                    And(str),
                                ],
                            } 
                        }]
                    }
                },
            ]
        }
    ],
    "graph": [
        { "from": Or(And(int, lambda x:x>0), And(str, lambda x:int(x)>0)), "to": Or(And(int, lambda x:x>0), And(str, lambda x:int(x)>0)) },
    ], 
    "path": And(str)
    })
    update(messages, result, result_schema)
    return json.loads(result)