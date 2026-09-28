"""
    模拟顺序执行
    time.sleep()用于模拟 HTTP 请求、数据库查询、第三方 API、网络等待
"""
import time
from utils.logger import log

def get_weather(city: str):
    log.info(f"开始查询 {city} 天气")
    time.sleep(2)

    return {
        "city": city,
        "temperature": 28,
        "weather": "晴",
    }


def get_time(city: str):
    log.info(f"开始查询 {city} 时间")
    time.sleep(1)

    return {
        "city": city,
        "time": "10:30",
    }


def get_exchange_rate(currency: str):
    log.info(f"开始查询 {currency} 汇率")
    time.sleep(3)

    return {
        "currency": currency,
        "rate": 7.2,
    }

start = time.perf_counter()

weather = get_weather("上海")
current_time = get_time("上海")
rate = get_exchange_rate("USD")

elapsed = time.perf_counter() - start

log.info(weather)
log.info(current_time)
log.info(rate)

log.info(f"总耗时：{elapsed:.2f} 秒")