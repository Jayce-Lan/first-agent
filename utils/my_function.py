"""
    用于存储常用方法
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from utils.constants import TIMEZONES
from utils.safe_eval import safe_eval


def get_weather(city: str):
    """
        获取天气
    """
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

def get_time(city: str):
    """
        获取时间
    """
    tz_name = TIMEZONES.get(city)
    if tz_name is None:
        time = f"未获取到当前城市[{city}]的时间"
    else:
        time = datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "city": city,
        "time": time
    }

def calculator(expression: str):
    """
        通过表达式求值
    """
    return {
        "expression": expression,
        "result": safe_eval(expression),
    }