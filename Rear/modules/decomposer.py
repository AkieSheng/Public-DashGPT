from utils.model import get_model_response, get_embedding
import json
from update import update
from schema import Schema, And, Or, Use, Optional, SchemaError


def retrieve_requirements(user_goal: str, database_description: str) -> list:
    with open('embedding/data_embeddings.json', 'r', encoding = 'utf-8') as file:
        data_text_set = json.load(file)
    with open('embedding/upddp-data.json', 'r', encoding = 'utf-8') as file:
        data = json.load(file)
    user_embedding = get_embedding(database_description + user_goal)
    data_text_list = list(data_text_set.keys())
    data_text_list.sort(key = lambda x: sum([a * b for a, b in zip(user_embedding, data_text_set[x])]), reverse = True)

    requirements = []
    for item in data:
        if item['data']['data_text'] in data_text_list[:3] and item['requirement']['requirement_text'] not in requirements:
            requirements.append(item['requirement']['requirement_text'])
    
    return requirements


def retrieve_solutions(user_goal: str, database_description: str) -> list:
    with open('embedding/data_embeddings.json', 'r', encoding = 'utf-8') as file:
        data_text_set = json.load(file)
    with open('embedding/upddp-data.json', 'r', encoding = 'utf-8') as file:
        data = json.load(file)
    user_embedding = get_embedding(database_description + user_goal)
    data_text_list = list(data_text_set.keys())
    data_text_list.sort(key = lambda x: sum([a * b for a, b in zip(user_embedding, data_text_set[x])]), reverse = True)

    solutions = []
    for item in data:
        if item['data']['data_text'] in data_text_list[:3] and item['solution'] not in solutions:
            solutions.append(item['solution'])
    
    return solutions


def decompose_goals(user_goal: str, database_info: dict, model: str = 'openai', use_rag: bool = True) -> dict:
    messages = [
        {
            'role': 'system',
            'content': open('prompts/goal_decomposition.txt', 'r').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False))
        },
        {
            'role': 'user',
            'content': 'The user\'s analysis goal is as follows: \n\n' + user_goal
        }
    ]
    if use_rag:
        used_requirements = retrieve_requirements(user_goal, database_info['description'])
        messages.append({
            'role': 'user',
            'content': 'In the past VA papers, there are some papers related to this database and analysis topic. Their design requirements are provided below, which can be used for reference.\n\n' + '\n\n'.join(used_requirements)
        })
    result = get_model_response(messages, model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()
    result_schema = Schema({
        "requirements": {
            "data": [
                { "id": And(str), "requirement": And(str), "reason":And(str) },
            ],
            "visualization": [
                { "id": And(str), "requirement": And(str), "reason": And(str) },
            ],
            "interaction": [
                { "id": And(str), "requirement": And(str), "reason": And(str) },

            ]
        }   
    })
    update(messages, result, result_schema)
    return json.loads(result)


def generate_tasks(user_goal: str, database_description: str, database_info: dict, requirements: dict, model: str = 'openai', use_rag: bool = True) -> dict:
    messages = [
        {
            'role': 'system',
            'content': open('prompts/task_generation.txt', 'r').read().replace('<TABLE INFORMATION HERE>', json.dumps(database_info, ensure_ascii = False)).replace('<USER GOAL HERE>', user_goal)
        },
        {
            'role': 'user',
            'content': 'The user\'s design requirements for the system is as follows:\n\n' + json.dumps(requirements, ensure_ascii = False)
        }
    ]
    if use_rag:
        used_solutions = retrieve_solutions(user_goal, database_description)
        messages.append({
            'role': 'user',
            'content': 'In the past VA papers, there are some papers related to this database and analysis topic. Their solutions are provided below, which can be used for reference when determining your tasks.\n\n' + json.dumps(used_solutions, ensure_ascii = False)
        })
    result = get_model_response(messages, model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()
    # 定义允许的字符串集合
    allowed_values = Or("retrieving values","filtering","computing derived values","finding extrema","sorting","determining ranges","characterizing distributions","finding anomalies","clustering" ,"correlating")

    result_schema = Schema({
        "tasks": [
            {
                "id": Or(And(int, lambda x:x>0), And(str, lambda x:int(x)>0)),
                "type": allowed_values,
                "data": And(list),
                "method": And(str),
                "objective": And(str),
                "corrReq": And(list),
                "priority": Or(And(int, lambda x:0<x<6), And(str, lambda x:0<int(x)<6)),
            },
        ] 
    })
    update(messages, result, result_schema)
    return json.loads(result)