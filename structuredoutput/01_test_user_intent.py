import asyncio
import orjson

from structuredoutput.user_intent import UserIntent
from utils.getclient_ollama import async_client
from utils.logger import log
from utils.json_utils import to_json
from utils.constants import OLLAMA_QWEN35_MODEL

async def classify(user_text: str) -> UserIntent:
    # 注意！ollama不支持client.chat.completions.create调用方式
    response = await async_client.chat.completions.create(
        model=OLLAMA_QWEN35_MODEL,
        messages=[
            {"role": "system", "content": (
                    "识别用户意图，只输出 JSON 对象，字段为 intent、order_id、reply。"
                    "intent 只能是 get_order、get_shipping、general。"
                    "如果没有订单号，order_id 填 null。"
                )},
            {"role": "user", "content": user_text}
        ],
        response_format={"type": "json_object"}
    )

    text = response.choices[0].message.content or ""
    log.info(to_json(response))
    log.info(f"用户意图识别结果: {text}")
    data = orjson.loads(text) # 第一步：验证JSON语法
    return UserIntent.model_validate(data) # 第二步：验证数据结构

async def main():
    result = await classify("我想查询订单1001的物流信息")
    log.info(f"识别结果: {to_json(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())