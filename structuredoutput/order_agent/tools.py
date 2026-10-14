"""
    模拟订单系统
    - `ORDERS` 模拟数据库。
    - `sleep` 模拟外部服务延迟。
    - 不存在的订单抛出 `ValueError`，由上层捕获。
    - `get_shipping` 依赖 `get_order`，体现工具之间的调用关系。
"""
import asyncio


ORDERS = {
    "1001": {
        "order_id": "1001",
        "status": "shipping",
        "tracking": "包裹已离开发货仓"
    },
    "1002": {
        "order_id": "1002",
        "status": "processing",
        "tracking": "订单正在处理中"
    },
}

async def get_order(order_id: str) -> dict:
    """
    获取订单信息
    """
    await asyncio.sleep(0.2)  # 模拟网络延迟
    order = ORDERS.get(order_id)
    if order is None:
        raise ValueError(f"订单 {order_id} 不存在")
    return order

async def get_shipping(order_id: str) -> dict:
    """
    获取订单物流信息
    """
    await asyncio.sleep(0.2)  # 模拟网络延迟
    order = await get_order(order_id)
    return {
        "order_id": order_id, 
        "tracking": order["tracking"]
    }