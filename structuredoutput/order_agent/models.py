"""
    结构化输出结果
    这是本地校验规则。模型负责生成数据，Pydantic 负责拒绝不符合约定的数据。结构合法仍不代表订单状态真实，真实状态必须由工具提供。
"""
from typing import Literal
from pydantic import BaseModel, Field


class UserIntent(BaseModel):
    intent: Literal["get_order", "get_shipping", "general"]
    order_id: str | None = Field(
        default=None,
        description="用户明确提供或从当前会话可靠取回的订单号"
    )
    reply: str = Field(description="简短的用户可读回复")