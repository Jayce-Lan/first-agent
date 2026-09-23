import os
from pathlib import Path

from agents import OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI

'''
    封装获取deepseek的key、model方法
'''


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"),
)

# 由于使用deepseek，因此需要重写原本属于openai的model
myModel = OpenAIChatCompletionsModel(
    model="deepseek-chat",
    openai_client=client
)