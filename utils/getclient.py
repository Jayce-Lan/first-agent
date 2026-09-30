
from pathlib import Path

import os
from dotenv import load_dotenv
from openai import OpenAI

'''
封装client
'''

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# 会自动读取 .env 里的 key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)