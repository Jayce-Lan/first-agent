import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from utils.logger import log


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# 会自动读取 .env 里的 key
client = OpenAI()

response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}}
)

log.info(response.choices[0].message.content)