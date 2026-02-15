import os
import sys

# 获取项目根目录的绝对路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 将项目根目录添加到 Python 路径
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# 设置环境变量
os.environ['DATABASE_PATH'] = os.path.join(PROJECT_ROOT)