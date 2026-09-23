'''
把tool output交还模型
'''
import orjson
from utils.getclient import client
from utils.logger import log
from utils.constants import DEFAULT_MODEL

def get_weather(city:str):
    """定义一个本地函数，存储天气信息

    Args:
        city: 传入城市
    Returns:
        返回城市天气情况
    """
    weather = {
        "南宁": {"temperature": 31, "condition": "晴"},
        "深圳": {"temperature": 28, "condition": "多云"},
        "新加坡": {"temperature": 31, "condition": "雷阵雨"},
    }
    return weather.get(
        city, 
        {"temperature": None, "condition": "暂无数据"}
        )

def call_function(name, args):
    """获取调用模型返回的arguments中的城市名称
    
    Args:
        name: 方法名
        args: arguments里存储城市名称的返回值
    Returns:
        返回get_weather调用结果
    Raises:
        城市不存在时抛出异常
    """
    if name == "get_weather":
        return get_weather(args["city"])
    raise ValueError(f"Unknown tool: {name}")

weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": "查询指定城市的当前天气。",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，例如南宁、深圳、新加坡"
            }
        },
        "required": ["city"],
        "additionalProperties": False
    },
    "strict": True
}

my_input = [
    {"role": "user", "content": "南宁现在天气怎么样？"}
]

tools = [weather_tool]

response = client.responses.create(
    model=DEFAULT_MODEL,
    tools=tools,
    input=my_input
)

for item in response.output:
    if item.type == "function_call":
        args = orjson.loads(item.arguments)
        result = call_function(item.name, args)
        log.info(f'工具结果: {result}') #  工具结果: {'temperature': 31, 'condition': '晴'}

        # 追加模型的 function_call 请求
        my_input.append(item)
        # 再追加工具的执行结果
        my_input.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": orjson.dumps(result).decode("utf-8")
        })

final_response = client.responses.create(
    model=DEFAULT_MODEL,
    tools=tools,
    input=my_input
)
log.info(final_response)
log.info(final_response.output_text)