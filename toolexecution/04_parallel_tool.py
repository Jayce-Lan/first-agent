import asyncio

import orjson

from utils.getclient_ollama import client
from utils.logger import log
from utils.constants import OLLAMA_QWEN35_MODEL
from utils.json_utils import to_json
from utils.my_async_function import get_weather, get_time, exexute_tool

TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_time": get_time,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市天气",
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
            "description": "查询指定城市时间",
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
]


async def execute_tools_parallel(tool_calls):
    """
        并行执行工具调用
    """

    results = await asyncio.gather(*[exexute_tool(tool_call, TOOL_REGISTRY) for tool_call in tool_calls])
    return results

async def run_agent(user_input:str):
    messages = [{"role": "user", "content": user_input}]

    while True:
        response = client.chat.completions.create(
            model=OLLAMA_QWEN35_MODEL,
            messages=messages,
            tools=tools,
        )

        log.info(f"response - {to_json(response)}")

        message = response.choices[0].message
        log.info(f"content - {message.content}")
        log.info(f"tool_calls - {message.tool_calls}")

        if message.tool_calls is None:
            return message.content

        results = await execute_tools_parallel(message.tool_calls)

        for item in results:
            messages.append({
                "tool_call_id": item["tool_call_id"],
                "role": "tool", 
                "content": orjson.dumps(item["result"]).decode("utf-8")
            })

async def main():
    user_input = "南宁、新加坡的天气如何？当前时间是什么？"
    final_result = await run_agent(user_input)
    log.info(f"最终结果 - {final_result}")

if __name__ == "__main__":
    asyncio.run(main())