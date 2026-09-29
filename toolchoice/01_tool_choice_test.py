"""
    查看none、auto、required各个模式的区别
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

def test(choice: str, user_input: str):
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

    log.info(f"{choice} response - {to_json(response)}")

    message = response.choices[0].message
    log.info(f"{choice} content - {message.content}")
    log.info(f"{choice} tool_calls - {message.tool_calls}")

test("auto", "你好")
test("auto", "南宁天气怎么样")
test("required", "你好")
test("none", "南宁天气怎么样")

"""
返回内容

2026-09-29 16:10:14 - 01_tool_choice_test.py(65) - INFO: auto response - {"id": "755e6406-8d46-4fc1-a3c8-0968113e2e29", "choices": [{"finish_reason": "stop", "index": 0, "message": {"content": "你好！😊 我是你的AI助手，很高兴见到你。\n\n我可以帮你查询城市天气，或者回答其他问题。有什么需要帮忙的吗？", "role": "assistant", "reasoning_content": "The user just said \"你好\" (hello). No tool calls needed. Just respond warmly.\n\nI could ask what they need. Let me respond in Chinese."}}], "created": 1790669413, "model": "deepseek-flash", "object": "chat.completion", "system_fingerprint": "aeb56401ca74e127821c4f9126dcb669", "usage": {"completion_tokens": 63, "prompt_tokens": 288, "total_tokens": 351, "completion_tokens_details": {"reasoning_tokens": 32}, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 160}}
2026-09-29 16:10:14 - 01_tool_choice_test.py(68) - INFO: auto content - 你好！😊 我是你的AI助手，很高兴见到你。

我可以帮你查询城市天气，或者回答其他问题。有什么需要帮忙的吗？
2026-09-29 16:10:14 - 01_tool_choice_test.py(69) - INFO: auto tool_calls - None
2026-09-29 16:10:14 - 01_tool_choice_test.py(65) - INFO: auto response - {"id": "3e92e7f1-4e3e-4668-a162-c0925616100f", "choices": [{"finish_reason": "tool_calls", "index": 0, "message": {"content": "", "role": "assistant", "tool_calls": [{"id": "call_00_IEnXdGESI32rXSwILnue6473", "function": {"arguments": "{\"city\": \"南宁\"}", "name": "get_weather"}, "type": "function", "index": 0}], "reasoning_content": "The user asks about Nanning weather. I should call get_weather with city \"南宁\"."}}], "created": 1790669414, "model": "deepseek-flash", "object": "chat.completion", "system_fingerprint": "aeb56401ca74e127821c4f9126dcb669", "usage": {"completion_tokens": 58, "prompt_tokens": 290, "total_tokens": 348, "completion_tokens_details": {"reasoning_tokens": 19}, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 162}}
2026-09-29 16:10:14 - 01_tool_choice_test.py(68) - INFO: auto content - 
2026-09-29 16:10:14 - 01_tool_choice_test.py(69) - INFO: auto tool_calls - [ChatCompletionMessageFunctionToolCall(id='call_00_IEnXdGESI32rXSwILnue6473', function=Function(arguments='{"city": "南宁"}', name='get_weather'), type='function', index=0)]
2026-09-29 16:10:15 - 01_tool_choice_test.py(65) - INFO: required response - {"id": "496831cc-2767-4b78-bc43-b331f2e3da69", "choices": [{"finish_reason": "tool_calls", "index": 0, "message": {"content": "", "role": "assistant", "tool_calls": [{"id": "call_00_8y7qWK5VoMikaSXfXJN28833", "function": {"arguments": "{\"city\": \"北京\"}", "name": "get_weather"}, "type": "function", "index": 0}]}}], "created": 1790669415, "model": "deepseek-flash", "object": "chat.completion", "system_fingerprint": "aeb56401ca74e127821c4f9126dcb669", "usage": {"completion_tokens": 33, "prompt_tokens": 269, "total_tokens": 302, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 141}}
2026-09-29 16:10:15 - 01_tool_choice_test.py(68) - INFO: required content - 
2026-09-29 16:10:15 - 01_tool_choice_test.py(69) - INFO: required tool_calls - [ChatCompletionMessageFunctionToolCall(id='call_00_8y7qWK5VoMikaSXfXJN28833', function=Function(arguments='{"city": "北京"}', name='get_weather'), type='function', index=0)]
2026-09-29 16:10:19 - 01_tool_choice_test.py(65) - INFO: none response - {"id": "bfca3007-b38b-49e7-949b-e7942971d2a7", "choices": [{"finish_reason": "stop", "index": 0, "message": {"content": "我无法实时联网获取南宁最新的天气数据，所以不能准确告诉你此刻或今天的实时天气。\n\n建议你打开手机天气 App，或到“中国天气网”搜索“南宁”查看最新预报。\n\n参考：5 月的南宁通常已经比较闷热，常年气温大约在 **22～30℃** 左右，降雨增多，常有阵雨或雷阵雨。出门建议带伞，注意防暑和防潮。  \n如果你告诉我具体日期，我可以帮你做一般的穿衣和出行建议。", "role": "assistant", "reasoning_content": "我们需要回答用户“南宁天气怎么样”。我们需要提供天气信息。需要知道当前日期？系统当前日期 2026-05-07。用户问南宁天气怎么样，通常需要实时天气。但我们无法联网。需要说明无法获取实时天气，建议查看天气预报。但也许可以给一般性气候信息？ 需要看政策？没有禁止。应该回答：我无法实时联网获取最新天气，当前南宁天气请以气象台为准。可以建议通过天气App/中国天气网查询。也可以提供5月南宁气候概况：气温约25-30°C，湿热，多雨，可能有雷阵雨，需带伞。如果用户需要，可以告诉我具体日期，我给出穿衣建议等。但用户期望具体天气。我们不能编造实时天气。应该简洁。\n\n需要中文回复。也许可以问是否要查今天/明天。可以给建议。最好提及当前日期2026-05-07，但天气是实时变化的，我无法提供。若需要，可以打开联网？作为API没有联网。可以建议“中国天气网、墨迹天气、weather.com.cn”等。我们可以说：南宁今天（5月7日）通常进入前汛期，天气闷热多雨。但具体温度、降雨无法确认。 \n\n需要遵守不编造。最终回答应直接。也许格式：\n“我无法实时获取南宁的最新天气数据，所以不能准确告诉你此刻/今天的天气。建议打开天气App或中国天气网搜索‘南宁’。参考：5月南宁已比较闷热，常年日温约22-30°C，降雨增多，常有阵雨/雷阵雨，出门带伞、注意防暑。如果你告诉我具体日期，我可以帮你做一般性穿衣/出行建议。”\n\n这不错。但可能用户期望我们回答。要确保没有误导。也许可以添加“如需实时，我建议查看：中国天气网、手机自带天气App”。最终答案长度适中。"}}], "created": 1790669416, "model": "deepseek-flash", "object": "chat.completion", "system_fingerprint": "aeb56401ca74e127821c4f9126dcb669", "usage": {"completion_tokens": 508, "prompt_tokens": 33, "total_tokens": 541, "completion_tokens_details": {"reasoning_tokens": 402}, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 33}}
2026-09-29 16:10:19 - 01_tool_choice_test.py(68) - INFO: none content - 我无法实时联网获取南宁最新的天气数据，所以不能准确告诉你此刻或今天的实时天气。

建议你打开手机天气 App，或到“中国天气网”搜索“南宁”查看最新预报。

参考：5 月的南宁通常已经比较闷热，常年气温大约在 **22～30℃** 左右，降雨增多，常有阵雨或雷阵雨。出门建议带伞，注意防暑和防潮。  
如果你告诉我具体日期，我可以帮你做一般的穿衣和出行建议。
2026-09-29 16:10:19 - 01_tool_choice_test.py(69) - INFO: none tool_calls - None
"""