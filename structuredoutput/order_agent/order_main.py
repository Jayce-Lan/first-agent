import asyncio

from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
import orjson
from pydantic import ValidationError

from utils.getclient_ollama import get_async_client
from utils.logger import log
from utils.json_utils import to_json
from utils.constants import OLLAMA_QWEN35_MODEL

from models import UserIntent
from memory import get_history, recall_order, remember_order
from tools import get_order, get_shipping

async_client = get_async_client(300)

"""
    1.Structured Output
    1.1. 固定 system prompt 放在最前面。
    1.2. 将历史对话作为 Context 传给模型。
    1.3. 请求 JSON mode（前提是当前 provider/model 支持）。
    1.4. `json.loads` 检查 JSON 语法。
    1.5. `model_validate` 检查字段与类型。
"""

async def classify_intent(history: list[dict]) -> UserIntent:
    system_prompt = (
        "识别用户最新消息的意图，只输出 JSON 对象，字段为 intent、order_id、reply。"
        "intent 只能是 get_order、get_shipping、general。"
        "如果最新消息没有订单号，可以使用历史中明确的订单号；"
        "如果无法确定，order_id 必须为 null。"
    )

    # 保持system指令在消息最前面，历史中的初始system消息不重复传入
    request_messages = [
        {"role": "system", "content": system_prompt},
        *history[1:],
    ]

    response = await async_client.chat.completions.create(
        model=OLLAMA_QWEN35_MODEL,
        messages=request_messages,
        response_format={"type": "json_object"},
    )

    log.info(f"classify_intent 返回参数response- {to_json(response)}")
    raw_text = response.choices[0].message.content or ""
    data = orjson.loads(raw_text)
    log.info(f"classify_intent 返回参数data- {to_json(data)}")
    return UserIntent.model_validate(data)

"""
    2.模型请求有限重试
    - `attempts=2` 表示总共最多尝试两次。
    - 仅对连接失败和超时重试。
    - 第一次失败等待 0.5 秒，之后若仍有下一次则等待时间增加。
    - JSON 格式错误和 Schema 校验错误没有自动重试，因为同样的请求重复发送未必会修复格式问题。
    - 生产环境还需根据服务商规则决定是否处理 429、5xx 和 `Retry-After`。
"""
async def classify_with_retry(history: list[dict], attempts: int = 2) -> UserIntent:
    """模型请求有限重试

    Args:
        history: 历史记录
        attempts: 表示总共最多尝试两次

    Returns:
        返回标准格式

    Raises:
        ValueError: 异常
    """
    for attempt in range(1, attempts + 1):
        try:
            return await classify_intent(history)
        except (APITimeoutError, APIConnectionError):
            if attempt == attempts:
                raise await asyncio.sleep(0.5 * (2 ** (attempt - 1)))
    raise RuntimeError("不应执行到此...")

"""
    3.执行意图和工具超时
    - 先使用本轮识别出的订单号；没有时再取回会话中最近的订单号。
    - 没有订单号时追问，不允许编造。
    - `asyncio.wait_for` 限制工具执行时间。
    - `ValueError` 是已知业务错误；其他异常返回通用信息，避免暴露内部细节。
"""

async def handle_intent(intent: UserIntent, session_id: str) -> str:
    order_id = intent.order_id or recall_order(session_id)

    if intent.intent == "general":
        return intent.reply

    if order_id is None:
        return "请先提供单号，例如 1001"

    remember_order(session_id, order_id)

    try:
        if intent.intent == "get_order":
            result = await asyncio.wait_for(get_order(order_id), timeout=2.0)
        else:
            result = await asyncio.wait_for(get_shipping(order_id), timeout=2.0)

    except asyncio.TimeoutError:
        return "订单服务响应超时，请稍后再试"
    except ValueError as exc:
        return str(exc)
    except Exception:
        # 生产环境应记录日志，但不要向用户暴露内部堆栈
        return "查询订单时发生暂时性错误，请稍后再试"

    return orjson.dumps(result).decode("utf-8")


"""
    4.主循环
    4.1. 接收输入。
    4.2. 通过 `session_id` 取回会话历史。
    4.3. 把当前用户消息追加进历史。
    4.4. 调模型得到结构化意图。
    4.5. 对模型连接错误/超时有限重试。
    4.6. 执行订单工具并捕获工具超时和业务错误。
    4.7. 将最终回复写回历史，为下一轮提供 Context。
"""
async def main():
    session_id = "demo-session"

    while True:
        user_text = input("\n你: ").strip()
        if user_text.lower() in {"q", "quit", "exit"}:
            break
        if user_text is None:
            continue

        history = get_history(session_id)
        history.append({"role": "user", "content": user_text})

        try:
            intent = await classify_with_retry(history)
            answer = await handle_intent(intent, session_id)
        except (APITimeoutError, APIConnectionError):
            answer = "模型服务暂时不可用，请稍后再试。"
        except (orjson.JSONDecodeError, ValidationError) as exc:
            answer = "我暂时无法解析这次请求，请换一种说法再试。"
            print(f"[调试] 结构化输出解析/校验失败：{type(exc).__name__}")
        except RateLimitError:
            answer = "模型服务请求过多，请稍后再试。"
        except APIStatusError as exc:
            answer = f"模型服务返回 HTTP {exc.status_code}，请稍后再试。"

        history.append({"role": "assistant", "content": answer})
        print("客服: ", answer)

if __name__ == "__main__":
    asyncio.run(main())