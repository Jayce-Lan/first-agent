"""
    测试本地ollama部署模型
"""
import orjson

from utils.getclient_ollama import client
from utils.logger import log
from utils.constants import OLLAMA_QWEN35_MODEL
from utils.json_utils import to_json
from utils.my_function import (get_weather, calculate_difference)

TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculate_difference": calculate_difference,
}

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
            "name": "calculate_difference",
            "description": (
                "比较两个城市的气温高低。"
                "需要提供两个城市各自的城市名和气温值。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city_a": {
                        "type": "object",
                        "description": "第一个城市的信息。",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称，例如南宁。"
                            },
                            "temperature": {
                                "type": "number",
                                "description": "该城市的气温，单位为摄氏度。"
                            }
                        },
                        "required": ["city", "temperature"],
                        "additionalProperties": False
                    },
                    "city_b": {
                        "type": "object",
                        "description": "第二个城市的信息。",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称，例如东京。"
                            },
                            "temperature": {
                                "type": "number",
                                "description": "该城市的气温，单位为摄氏度。"
                            }
                        },
                        "required": ["city", "temperature"],
                        "additionalProperties": False
                    }
                },
                "required": ["city_a", "city_b"],
                "additionalProperties": False
            }
        }
    }
]

messages = [
    {
        "role": "user",
        "content": "南宁、新加坡的天气如何？比较一下两地天气。"
    }
]

while True:
    response = client.chat.completions.create(
        model=OLLAMA_QWEN35_MODEL,
        messages=messages,
        tools=tools
    )

    log.info(f"response - {orjson.dumps(response.model_dump()).decode("utf-8")}")
    message = response.choices[0].message
    messages.append(message)

    log.info(f"messages - {to_json(messages)}")

    if message.tool_calls is None:
        log.info(f"输出最终结果 - {message.content}")
        break

    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        arguments = orjson.loads(tool_call.function.arguments)

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