"""
    用于存储常用方法
"""

import orjson
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.constants import TIMEZONES
from utils.logger import log


async def get_weather(city: str):
    """
        获取天气
    """
    log.info(f"[tool] 执行get_weather - city: {city}")
    await asyncio.sleep(2)  # 模拟耗时操作
    log.info(f"[tool] get_weather - city: {city} 执行完成")

    weather_data = {
            "东京": {
                "temperature": 26,
                "weather": "晴",
            },
            "南宁": {
                "temperature": 31,
                "weather": "晴",
            },
            "新加坡": {
                "temperature": 30,
                "weather": "雷阵雨",
            },
            "纽约": {
                "temperature": 25,
                "weather": "多云",
            },
        }
    
    return {"city": city, **weather_data.get(city)}

async def get_time(city: str):
    """
        获取时间
    """
    log.info(f"[tool] 执行get_time - city: {city}")
    await asyncio.sleep(1)  # 模拟耗时操作
    log.info(f"[tool] get_time - city: {city} 执行完成")

    tz_name = TIMEZONES.get(city)
    if tz_name is None:
        time = f"未获取到当前城市[{city}]的时间"
    else:
        time = datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "city": city,
        "time": time
    }

async def exexute_tool(tool_call, tool_registry):
    """
        执行工具函数
    """
    tool_name = tool_call.function.name

    arguments = orjson.loads(tool_call.function.arguments)
    function = tool_registry.get(tool_name)
    if function is None:
        return {
            "tool_call_id": tool_call.id,
            "result": {"error": f"未知工具：{tool_name}"}
        }

    try:
        result = await function(**arguments)

        return {
            "tool_call_id": tool_call.id,
            "result": result
        }

    except Exception as e:
        return {
            "tool_call_id": tool_call.id,
            "result": {"error": str(e)}
        }
    
