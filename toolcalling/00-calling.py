'''
    第一步：调用模型
'''
import orjson
from utils.getclient import client
from utils.logger import log
from utils.constants import DEFAULT_MODEL

response = client.responses.create(
    model=DEFAULT_MODEL,
    input="请介绍一下什么是tool calling。"
)

log.info(orjson.dumps(response.model_dump()).decode("utf-8"))
log.info(response.output_text)