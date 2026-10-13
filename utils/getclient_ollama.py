from pathlib import Path

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

'''
封装client
'''

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# 会自动读取 .env 里的 key
client = OpenAI(
    api_key=os.getenv("OLLAMA_API_KEY"),
    base_url=os.getenv("OLLAMA_API_URL")
)

async_client = AsyncOpenAI(
    api_key=os.getenv("OLLAMA_API_KEY"),
    base_url=os.getenv("OLLAMA_API_URL"),
    timeout=20.0,  # 单次模型 HTTP 请求超时
    max_retries=0, # 本教程手动演示错误处理
)