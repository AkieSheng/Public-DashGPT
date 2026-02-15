from schema import Schema, And, Or, Use, Optional, SchemaError
import tiktoken
import json
def update(message, result, result_schema):
    with open('data.json', 'r', encoding='utf-8') as file:
        data_new = json.load(file)
                
    try:
        validated_data = result_schema.validate(json.loads(result))
        print("数据验证通过:", validated_data)
    except SchemaError as e:
        print("数据验证失败:", e)
        data_new[-1]['data'][-1]['data'][-1]['format_error'] += 1
        print(json.loads(result))
    encoding = tiktoken.encoding_for_model("gpt-4o")
    
    # 如果数据不是字符串，将其转换为字符串
    if not isinstance(result, str):
        t_result = json.dumps(result, ensure_ascii=False)
    else:
        t_result = result
    # 计算 token 数
    otokens = encoding.encode(t_result)
    data_new[-1]['data'][-1]['data'][-1]['otoken'] += len(otokens)
    
    if not isinstance(message, str):
        t_message = json.dumps(message, ensure_ascii=False)
    else:
        t_message = result
    # 计算 token 数
    itokens = encoding.encode(t_message)
    data_new[-1]['data'][-1]['data'][-1]['itoken'] += len(itokens)
                
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data_new, file, ensure_ascii=False, indent=4)