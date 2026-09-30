import orjson

from utils.getclient import client
from utils.logger import log
from utils.constants import DEFAULT_MODEL
from utils.json_utils import to_json
from toolchoice.toolchoice_orders_demo.tools import (get_order, get_shipping, calculate_refund)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "根据订单号查询订单信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_shipping",
            "description": "根据物流单号查询物流状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "shipping_id": {
                        "type": "string"
                    }
                },
                "required": ["shipping_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "calculate_refund",
            "description": "根据价格和使用天数计算退款",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {
                        "type": "number"
                    },
                    "used_days": {
                        "type": "integer"
                    }
                },
                "required": [
                    "price",
                    "used_days"
                ]
            }
        }
    }
]

TOOL_REGISTRY = {
    "get_order": get_order,
    "get_shipping": get_shipping,
    "calculate_refund": calculate_refund
}

def execute_tool(tool_call):
    name = tool_call.function.name
    arguments = orjson.loads(tool_call.function.arguments)

    function = TOOL_REGISTRY.get(name)

    log.info(f"execute_tool - name - {name}")
    log.info(f"execute_tool - arguments - {arguments}")
    log.info(f"execute_tool - arguments type - {type(arguments)}")
    log.info(f"execute_tool - function - {function}")

    if function is None:
        return {"error": f"未知工具{name}"}

    try:
        return function(**arguments)
    except Exception as e:
        return {"error": str(e)}

def run_agent(user_input: str, tool_choice: str = "auto", max_steps: int = 10):
    messages = [
        {
            "role": "user",
            "content": user_input
        },
        {
            "role": "system",
            "content": "你是一个订单客服Agent，可以查询订单、物流、计算退款，需要真实数据时必须使用工具"
        }
    ]

    for step in range(max_steps):
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice=tool_choice
        )

        message = response.choices[0].message

        messages.append(message)

        log.info(f"========={step}==========")
        log.info(f"tool_choice: {tool_choice}")
        log.info(f"response - {to_json(response)}")
        log.info(f"messages - {to_json(messages)}")
        log.info(f"content - {message.content}")
        log.info(f"tool_calls - {to_json(message.tool_calls)}")

        if message.tool_calls is None:
            return message.content

        for tool_call in message.tool_calls:
            result = execute_tool(tool_call)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": orjson.dumps(result).decode("utf-8")
            })

    return f"Agent 超过最大执行步数，停止执行。"

