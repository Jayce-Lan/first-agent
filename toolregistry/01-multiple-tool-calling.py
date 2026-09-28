'''
    Multiple Tool Calling 的完整执行过程
'''

from datetime import datetime
from zoneinfo import ZoneInfo

import orjson
from utils.getclient import client
from utils.logger import log
from utils.constants import DEEPSEEK_FLASH_MOEDL, TIMEZONES
from utils.json_utils import to_json
from utils.safe_eval import safe_eval

def get_weather(city: str):
    """
        获取天气
    """
    weather_data = {
            "东京": {
                "temperature": 26,
                "weather": "晴",
            },
            "南宁": {
                "temperature": 31,
                "weather": "晴",
            },
            "新加坡": {
                "temperature": 30,
                "weather": "雷阵雨",
            },
            "纽约": {
                "temperature": 25,
                "weather": "多云",
            },
        }
    
    return {"city": city, **weather_data.get(city)}


def get_time(city: str):
    """
        获取时间
    """
    tz_name = TIMEZONES.get(city)
    if tz_name is None:
        time = f"未获取到当前城市[{city}]的时间"
    else:
        time = datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "city": city,
        "time": time
    }

def calculator(expression: str):
    """
        通过表达式求值
    """
    return {
        "expression": expression,
        "result": safe_eval(expression),
    }

TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_time": get_time,
    "calculator": calculator,
}

# Tools Schema

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称",
                    }
                },
                "required": ["city"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "查询城市当前时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称",
                    }
                },
                "required": ["city"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 20*3+5",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]

messages = [
    {
        "role": "user",
        "content": "南宁、新加坡的天气如何？现在几点？"
    }
]

while True:
    response = client.chat.completions.create(
        model=DEEPSEEK_FLASH_MOEDL,
        messages=messages,
        tools=tools
    )

    log.info(f"response - {orjson.dumps(response.model_dump()).decode("utf-8")}")
    
    message = response.choices[0].message
    messages.append(message)
    log.info(f"messages - {to_json(messages)}")

    if not message.tool_calls:
        log.info(f"输出最终结果: {message.content}")
        break

    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        arguments = orjson.loads(tool_call.function.arguments)

        # 根据被管理的tool去调用
        function = TOOL_REGISTRY.get(tool_name)

        if function is None:
            result = {"error": f"未知工具：{tool_name}"}
        else:
            try:
                result = function(**arguments)
            except Exception as e:
                result = {"error": str(e)}

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": orjson.dumps(result).decode("utf-8")
        })