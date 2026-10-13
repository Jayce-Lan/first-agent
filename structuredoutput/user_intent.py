"""
    结构化输出结果
    - `BaseModel` 是 Pydantic 的数据模型基类。
    - `intent` 只能是三个值之一，避免业务代码处理任意字符串。
    - `order_id` 允许字符串或 `None`，因为用户可能还没提供订单号。
    - `reply` 是简短的用户可读回复。
"""
from typing import Literal
from pydantic import BaseModel

class UserIntent(BaseModel):
    intent: Literal["get_order", "get_shipping", "general"]
    order_id: str | None
    reply: str