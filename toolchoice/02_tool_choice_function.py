"""
    使用指定function
"""
from utils.getclient import client
from utils.logger import log
from utils.constants import DEFAULT_MODEL, THINKING_TYPE_ENABLED_TOOL_CHOICE
from utils.json_utils import to_json

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    }
]

def test(choice, user_input: str):
    # 如果不是auto/none，则关闭思考模式，默认打开
    thinking_type = "enabled"
    if choice not in THINKING_TYPE_ENABLED_TOOL_CHOICE:
        thinking_type = "disabled"

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": user_input}],
        tools=tools,
        tool_choice=choice,
        extra_body={"thinking": {"type": thinking_type}} # 思考模式开关
    )

    log.info(f"response - {to_json(response)}")

    message = response.choices[0].message
    log.info(f"content - {message.content}")
    log.info(f"tool_calls - {message.tool_calls}")

choice = {
    "type": "function", 
    "function": {
        "name": "get_weather"
    }
}

test(choice, "你好")

"""
输出结果

2026-09-29 16:59:17 - 02_tool_choice_function.py(40) - INFO: response - {"id": "6909b181-b6c1-4d54-98e5-00897bfbfa74", "choices": [{"finish_reason": "tool_calls", "index": 0, "message": {"content": "","role": "assistant", "tool_calls": [{"id": "call_00_Ebe2l75U2BnZfNlzMCEU7423", "function": {"arguments": "{\"city\": \"北京\"}", "name": "get_weather"}, "type": "function", "index": 0}]}}], "created": 1790672356, "model": "deepseek-flash", "object": "chat.completion", "system_fingerprint": "aeb56401ca74e127821c4f9126dcb669", "usage": {"completion_tokens": 33, "prompt_tokens": 269, "total_tokens": 302, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 141}}
2026-09-29 16:59:17 - 02_tool_choice_function.py(43) - INFO: content - 
2026-09-29 16:59:17 - 02_tool_choice_function.py(44) - INFO: tool_calls - [ChatCompletionMessageFunctionToolCall(id='call_00_Ebe2l75U2BnZfNlzMCEU7423', function=Function(arguments='{"city": "北京"}', name='get_weather'), type='function', index=0)]
"""