'''
    完整最小Agent Loop
'''
import orjson
from utils.getclient import client
from utils.logger import log
from utils.constants import DEEPSEEK_FLASH_MOEDL

WEATHER = {
    "南宁": {"condition": "晴", "temperature_c": 31},
    "北京": {"condition": "晴", "temperature_c": 25},
    "新加坡": {"condition": "多云", "temperature_c": 30},
}

def get_weather(city: str) -> dict:
    if city not in WEATHER:
        return {"error": "没有这个城市的演示天气"}
    # 这里使用**是为了把对应城市的字典平铺，即最终格式为：{"city": city, "condition": "晴", "temperature_c": 31, "source": "固定演示数据"}
    return {"city": city, **WEATHER[city], "source": "固定演示数据"}

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询字典值所拥有的城市的固定演示天气，并非实时天气。",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
            "additionalProperties": False,
        },
    },
}]

def run_agent(question: str, max_rounds: int = 5) -> str:
    """
        模型可能在第一轮同时请求北京、南宁、新加坡等个天气，也可能先请求一个再请求另一个。两种都属于正常行为
    """
    # messages 初始只有系统说明和用户提问。它是这次任务的“对话本”。DeepSeek 的多轮 Chat Completions 需要程序自行管理并再次传入历史消息。
    messages = [
        {"role": "system", "content": "只能依据工具结果报告演示天气，不得称其为实时天气。"},
        {"role": "user", "content": question},
    ]

    for round_no in range(1, max_rounds + 1):
        response = client.chat.completions.create(
            model=DEEPSEEK_FLASH_MOEDL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        log.info(f'第{round_no}轮循环中的choice：{orjson.dumps(response.model_dump()).decode("utf-8")}')
        choice = response.choices[0]
        assistant_message = choice.message
        calls = assistant_message.tool_calls or []
        log.info(f'第{round_no}轮：finsh_reason={choice.finish_reason}，工具数={len(calls)}')

        if choice.finish_reason == "length":
            raise RuntimeError("模型输出被截断，不执行可能不完整的参数")
        if choice.finish_reason not in ("stop", "tool_calls"):
            raise RuntimeError(f"模型未完成：{choice.finish_reason}")

        if not calls:
            return assistant_message.content or "模型未返回文字"

        # 把带tool_calls的assistant原消息写回历史（类似把Tool output交还模型）
        messages.append(assistant_message.model_dump(exclude_none=True))

        for call in calls:
            try:
                if call.function.name != "get_weather":
                    raise ValueError("未知工具")
                arguments = orjson.loads(call.function.arguments)
                if not isinstance(arguments, dict) or set(arguments) != {"city"}:
                    raise ValueError("参数必须且只能有city")
                city = arguments["city"]
                if not isinstance(city, str) or not city.strip():
                    raise ValueError("city必须为非空字符串")
                result = get_weather(city.strip())
            except(ValueError, TypeError, KeyError) as exc:
                result = {"error": str(exc)}

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": orjson.dumps(result).decode("utf-8"),
            })
            log.info(f"执行工具：{call.function.name}, 结果：{result}")

    raise RuntimeError(f"超过{max_rounds}轮，已停止")

if __name__ == "__main__":
    log.info(run_agent("北京、南宁、上海、新加坡的天气分别是什么？"))