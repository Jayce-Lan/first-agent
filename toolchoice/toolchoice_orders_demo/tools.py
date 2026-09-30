ORDERS = {
    "10001": {
        "order_id": "10001",
        "product": "机械键盘",
        "price": 399,
        "status": "已发货",
        "shipping_id": "SF123456"
    },
    "10002": {
        "order_id": "10002",
        "product": "无线鼠标",
        "price": 199,
        "status": "运输中",
        "shipping_id": "SF654321"
    }
}


SHIPPING = {
    "SF123456": {
        "company": "顺丰",
        "status": "运输中",
        "location": "上海"
    },
    "SF654321": {
        "company": "顺丰",
        "status": "派送中",
        "location": "深圳"
    }
}

def get_order(order_id: str):
    return ORDERS.get(
        order_id,
        {"error": "订单不存在"}
    )


def get_shipping(shipping_id: str):
    return SHIPPING.get(
        shipping_id,
        {"error": "物流单号不存在"}
    )

def calculate_refund(price: float, used_days: int):

    if price < 0:
        return {"error": "价格不能为负数"}

    if used_days < 0:
        return {"error": "使用天数不能为负数"}

    if used_days <= 7:
        refund = price
    elif used_days <= 30:
        refund = price * 0.8
    else:
        refund = 0

    return {
        "price": price,
        "used_days": used_days,
        "refund": refund
    }

