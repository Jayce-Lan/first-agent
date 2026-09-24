'''
    测试调用LLM返回
'''
import orjson
from utils.getclient import client
from utils.logger import log
from utils.constants import DEEPSEEK_FLASH_MOEDL

def get_weather(city: str):
    weather_data = {
        "北京": {
            "temperature": 26,
            "weather": "晴",
        },
        "南宁": {
            "temperature": 31,
            "weather": "晴",
        },
        "深圳": {
            "temperature": 30,
            "weather": "雷阵雨",
        },
    }

    return weather_data.get(
        city,
        {
            "temperature": None,
            "weather": "未知",
        }
    )

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如北京、南宁、深圳",
                    }
                },
                "required": ["city"],
            },
        },
    }
]

messages = [
    {
        "role": "user",
        "content": "南宁今天天气怎么样？"
    }
]

response = client.chat.completions.create(
    model=DEEPSEEK_FLASH_MOEDL,
    messages=messages,
    tools=tools,
)

'''
    模型并不返回{"temperature": 31,"weather": "晴",}，而是返回
    "tool_calls": [
                        {
                            "id": "call_00_cNtRkz4X5dfVxZ1SYkIV6921",
                            "function": {
                                "arguments": "{\"city\": \"南宁\"}",
                                "name": "get_weather"
                            },
                            "type": "function",
                            "index": 0
                        }
                    ]
    即，模型告诉你，它要调用 get_weather，参数是{"city": "南宁"}
'''
log.info(orjson.dumps(response.model_dump()).decode("utf-8"))
log.info(response.choices[0].message)