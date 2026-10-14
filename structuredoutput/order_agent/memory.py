"""
- `SESSIONS` 保存对话历史。
- `SESSION_STATE` 保存可直接读取的业务状态。
- 二者用途不同：历史有助于理解自然语言，结构化状态更可靠地保存订单号。
- 当前是进程内内存，重启会丢失；生产环境应持久化。
"""

from utils.logger import log
from utils.json_utils import to_json

SESSIONS: dict[str, list[dict]] = {}
SESSION_STATE: dict[str, dict] = {}

def get_history(session_id: str) -> list[dict]:
    """
    获取对话历史
    """
    if session_id not in SESSIONS:
        SESSIONS[session_id] = [
            {
                "role": "system",
                "content": (
                    "你是一个订单查询助手。"
                    "只根据对话和工具结果回答，不要编造订单状态。"
                )
            }
        ]
    log.info(f"获取对话历史，会话: {session_id}，当前历史: {to_json(SESSIONS)}")
    return SESSIONS[session_id]

def remember_order(session_id: str, order_id: str) -> None:
    """
    记住订单号
    """
    SESSION_STATE.setdefault(session_id, {})["last_order_id"] = order_id
    log.info(f"记住订单号: {order_id}，会话: {session_id}，当前状态: {to_json(SESSION_STATE)}")

def recall_order(session_id: str) -> str | None:
    """
    回忆订单号
    """
    log.info(f"回忆订单号，会话: {session_id}，当前状态: {to_json(SESSION_STATE)}")
    return SESSION_STATE.get(session_id, {}).get("last_order_id")