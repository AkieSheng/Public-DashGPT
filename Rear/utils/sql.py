import sqlite3
import pandas as pd
import os


def csv_to_sqlite(path: str, output: str):
    # Create new DB file
    conn = sqlite3.connect(output)

    for csv_file in os.listdir(path):
        if not csv_file.endswith('.csv'):
            continue
        table_name = csv_file.split('.')[0]
        df = pd.read_csv(os.path.join(path, csv_file))
        df.to_sql(table_name, conn, if_exists = 'replace', index = False)

    conn.commit()
    conn.close()


def get_intermediate_table(cursor: sqlite3.Cursor, conn: sqlite3.Connection, sql: str, table_name: str):
    # 执行 SQL 语句（该语句会生成一个名为 table_name 的视图，然后将该视图存储到 tables/table_name.csv）
    cursor.execute(f'DROP VIEW IF EXISTS {table_name}')
    cursor.execute(sql)
    conn.commit()
    # 读取视图
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
    # 将视图存储到 tables/table_name.csv
    df.to_csv(f'tables/{table_name}.csv', index = False)