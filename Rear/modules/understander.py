from sqlite3 import Cursor, Connection
import pandas as pd
import math
import json
from utils.model import get_model_response
from update import update
from schema import Schema, And, Or, Use, Optional, SchemaError
def understand_database(cursor: Cursor, conn: Connection, desc: str, model: str = 'openai') -> dict:
    # 获取数据库的所有表名及其对应的列名，及各列的数据类型
    database_info = []
    cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = cursor.fetchall()
        # 利用 pandas，进一步获取各列的统计信息、值的个数和不重复值的个数，并且列举每个列去重后的前 5 行数据
        df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
        stats = df.describe(include = 'all').to_dict()
        for column in columns:
            stats[column[1]]['samples'] = list(df[column[1]].value_counts().to_dict().keys())[:5]
        database_info.append({
            'table': table_name,
            'columns': [
                {
                    'name': column[1],
                    'dtype': column[2],
                    'stats': {
                        key: value for key, value in stats[column[1]].items() if type(value) != float or not math.isnan(value)
                    }
                } for column in columns
            ]
        })

    message = [
        {
            'role': 'system',
            'content': open('prompts/database_understanding.txt', 'r').read()
        },
        {
            'role': 'user',
            'content': json.dumps({
                'userDescription': desc,
                'databaseInfo': database_info
            }, ensure_ascii = False)
        }
    ]

    result = get_model_response(message, model = model)

    if result.startswith('```json'):
        result = result[8:-3].strip()

    result_schema = Schema({
        "tables": [
            {
                "table": And(str),
                "columns": [
                    {
                        "column": And(str),
                        "description": And(str)
                    }
                ]
            }
        ]
    })
    update(message, result, result_schema)
    result = json.loads(result)

    for i in range(len(result['tables'])):
        for j in range(len(result['tables'][i]['columns'])):
            database_info[i]['columns'][j].update(result['tables'][i]['columns'][j])

    

    return {'tables': database_info}
    