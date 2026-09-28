"""
    使用`asyncio.gather()`并行多个异步任务
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

    # any = await asyncio.gather(
    #     get_weather("上海"),
    #     get_time("上海"),
    # )

    # log.info(any) # [{'city': '上海', 'temperature': 28, 'weather': '晴'}, {'city': '上海', 'time': '10:30'}]

    weather, current_time = await asyncio.gather(
        get_weather("上海"),
        get_time("南宁")
    )

    log.info(weather)
    log.info(current_time)

    elapsed = time.perf_counter() - start
    log.info(f"总耗时：{elapsed:.2f} 秒")


if __name__ == "__main__":
    asyncio.run(main())