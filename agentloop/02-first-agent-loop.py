'''
    Agent Loop第一版
'''
import orjson
from utils.getclient import client
from utils.logger import log
from utils.constants import DEEPSEEK_FLASH_MOEDL
from utils.json_utils import to_json

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
        "content": "南宁和深圳今天天气怎么样？"
    }
]

# 根据LLM调用Tool的情况决定是否循环
while True:
    response = client.chat.completions.create(
        model=DEEPSEEK_FLASH_MOEDL,
        messages=messages,
        tools=tools,
    )

    log.info(f"response - {orjson.dumps(response.model_dump()).decode("utf-8")}")

    message = response.choices[0].message
    # 1. 把 assistant 的响应加入历史
    messages.append(message)

    log.info(f"messages - {to_json(messages)}")

    # 2. 没有 Tool Call，说明模型已经可以直接回答，并结束Agent Loop
    if not message.tool_calls:
        log.info(f"tool_calls已为空，可以输出结果：{message.content}")
        break

    # 3. 执行所有 Tool Call
    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        arguments = orjson.loads(tool_call.function.arguments)

        if tool_name == "get_weather":
            result = get_weather(arguments["city"])
        else:
            result = {"error": f"未知工具：{tool_name}"}

        # 4. 将结果返回给模型
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": orjson.dumps(result).decode("utf-8")
        })