'''
定义第一个tool
'''
import orjson
from utils.getclient import client
from utils.logger import log
from utils.constants import DEFAULT_MODEL

def get_weather(city:str):
    """定义一个本地函数，存储天气信息

    Args:
        city: 传入城市
    Returns:
        返回城市天气情况
    """
    weather = {
        "南宁": {"temperature": 31, "condition": "晴"},
        "深圳": {"temperature": 28, "condition": "多云"},
        "新加坡": {"temperature": 31, "condition": "雷阵雨"},
    }
    return weather.get(
        city, 
        {"temperature": None, "condition": "暂无数据"}
        )

# 模型并不知道这个 Python 函数的存在。我们还需要把“工具说明”告诉模型
'''
字段                     作用
type                    工具类型。Function Tool 使用 function。
name                    模型调用时使用的函数名。
description             告诉模型什么时候应该使用这个工具。
parameters              描述工具参数的 JSON Schema。
properties              每个参数的定义。
required                哪些参数必须提供。
additionalProperties    通常在 strict 模式下设置为 false。
strict                  让工具参数更加严格地遵循 Schema。
'''
weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": "查询指定城市的当前天气。",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，例如南宁、深圳、新加坡"
            }
        },
        "required": ["city"],
        "additionalProperties": False
    },
    "strict": True
}

# 让模型产生tool，但是模型只是提出调用请求，它没有执行你的 Python 函数
response = client.responses.create(
    model=DEFAULT_MODEL,
    tools=[weather_tool],
    input="南宁的天气如何？"
)

for item in response.output:
    # log.info(item)
    log.info(orjson.dumps(item.model_dump()).decode("utf-8"))

'''
    由于并没有执行函数，因此返回如下：
    {
        "arguments": "{\"city\": \"南宁\"}",
        "call_id": "call_00_3F5sOwbapIpbaauCCijd4387",
        "name": "get_weather",
        "type": "function_call",
        "id": "2e50367c-1959-427d-89c0-07348814dfae",
        "async_": null,
        "caller": null,
        "namespace": null,
        "status": "completed"
    }
'''
