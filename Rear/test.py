from modules.agent import NewExplorationThread
from modules.decomposer import retrieve_solutions
from pathlib import Path
import json
import os
import pandas as pd

AGENT_TEST_DIR = Path("agent_test")
os.makedirs(AGENT_TEST_DIR, exist_ok=True)

with open('cases.json', 'r', encoding='utf-8') as file:
    cases = json.load(file)

metrics_columns = [
    'database', 'analysis_goal', 'iteration', 'rag',
    'format_error', 'total_sql', 'total_error_sql',
    'total_vl', 'total_error_vl', 'total_steps',
    'vl_steps', 'vl_error_steps'
]

metrics_data = []

for db in cases:
    print(f"Testing database: {db['database']}")
    db_path = f"{db['database']}.db"

    for ag in db['ag']:
        print(f"Testing analysis goal: {ag[:50]}...")

        for iteration in range(3):
            print(f"Iteration {iteration + 1}")

            for use_rag in [False, True]:
                rag_status = "RAG_ON" if use_rag else "RAG_OFF"
                print(f"Testing with {rag_status}")

                va_id = f"{db['database']}_{iteration + 1}_{rag_status}"

                solutions = retrieve_solutions(ag, db['desc'])

                exploration = NewExplorationThread(
                    db_path=str(db_path),
                    desc=db['desc'],
                    goal=ag,
                    result_id=va_id,
                    use_reflect=False,
                    use_rag=use_rag,
                    models={
                        "database": "gpt-4o",
                        "requirements": "gpt-4o",
                        "tasks": "gpt-4o",
                        "plan": "gpt-4o",
                        "sql": "qwen-coder",
                        "vega": "qwen-coder"
                    }
                )

                evaluation_result = exploration.explore()

                result_file_path = AGENT_TEST_DIR / f"{va_id}_result.json"
                with open(result_file_path, 'w', encoding='utf-8') as result_file:
                    json.dump({
                        "outputs": exploration.outputs,
                        "evaluation": evaluation_result,
                        "dataset": exploration.dataset,
                        "retrieved_solutions": solutions
                    }, result_file, ensure_ascii=False, indent=4)

                metrics_row = {
                    'database': db['database'],
                    'analysis_goal': ag,
                    'iteration': iteration + 1,
                    'rag': use_rag,
                    'format_error': evaluation_result.get('failed_format_following', 0),
                    'total_sql': evaluation_result.get('total_sql', 0),
                    'total_error_sql': evaluation_result.get('total_error_sql', 0),
                    'total_vl': evaluation_result.get('total_vl', 0),
                    'total_error_vl': evaluation_result.get('total_error_vl', 0),
                    'total_steps': evaluation_result.get('total_steps', 0),
                    'vl_steps': evaluation_result.get('total_vl', 0),
                    'vl_error_steps': evaluation_result.get('total_error_vl', 0)
                }
                metrics_data.append(metrics_row)

                metrics_df = pd.DataFrame(metrics_data, columns=metrics_columns)
                metrics_df.to_csv(AGENT_TEST_DIR / "metrics.csv", index=False)

                with open(AGENT_TEST_DIR / "metrics.json", 'w', encoding='utf-8') as metrics_file:
                    json.dump(metrics_data, metrics_file, ensure_ascii=False, indent=4)

print("Testing complete. Metrics saved to agent_test directory.")