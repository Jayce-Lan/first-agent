'''
    测试链接
'''
import orjson
from utils.getclient import client
from utils.logger import log
from utils.constants import DEEPSEEK_FLASH_MOEDL

result = client.chat.completions.create(
    model=DEEPSEEK_FLASH_MOEDL,
    messages=[{"role": "user", "content": "请描述一下什么是Agent Loop"}]
)

# ChatCompletion 是 Pydantic 模型，.model_dump() 会把它转成普通 dict，orjson 就能序列化了。
log.info(orjson.dumps(result.model_dump()).decode("utf-8"))
log.info(result.choices[0].message.content)