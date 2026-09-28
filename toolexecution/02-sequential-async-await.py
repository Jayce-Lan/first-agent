"""
    使用async定义异步函数，并使用await使之顺序执行
"""
import asyncio, time
from utils.logger import log

async def get_weather(city: str):

    log.info(f"开始查询 {city} 天气")

    await asyncio.sleep(2)

    return {
        "city": city,
        "temperature": 28,
        "weather": "晴",
    }


async def get_time(city: str):

    log.info(f"开始查询 {city} 时间")

    await asyncio.sleep(1)

    return {
        "city": city,
        "time": "10:30",
    }

async def main():
    start = time.perf_counter()
    weather = await get_weather("上海")
    log.info(weather)

    current_time = await get_time("上海")
    log.info(current_time)

    elapsed = time.perf_counter() - start
    log.info(f"总耗时：{elapsed:.2f} 秒")


if __name__ == "__main__":
    asyncio.run(main())