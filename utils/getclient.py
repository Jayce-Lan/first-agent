
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

'''
封装client
'''

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# 会自动读取 .env 里的 key
client = OpenAI()