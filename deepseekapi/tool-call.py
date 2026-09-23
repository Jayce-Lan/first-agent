import json
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from utils.logger import log

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# 会自动读取 .env 里的 key
client = OpenAI()

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

'''
这个例子的执行流程如下：

用户：询问现在的天气
模型：返回 function get_weather({location: 'Hangzhou'})
用户：调用 function get_weather({location: 'Hangzhou'})，并传给模型。
模型：返回自然语言，"The current temperature in Hangzhou is 24°C."
注：代码中 get_weather 函数功能需由用户提供，模型本身不执行具体函数。
'''

# 1.定义工具，告知模型有哪些函数可用
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.", # 给模型看的说明
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, Nanning, Guangxi",
                    }
                },
                "required": ["location"] # 必传参数
            },
        }
    },
]

# 2.第一次调用模型
messages = [{"role": "user", "content": "How's the weather in Nanning, Guangxi?"}]
message = send_messages(messages)

'''
返回内容
注意：content 通常是 null，真正有用的是 tool_calls。

ChatCompletionMessage(content="I'll check that for you.", 
refusal=None, 
role='assistant', 
annotations=None, 
audio=None, 
function_call=None, 
tool_calls=[ChatCompletionMessageFunctionToolCall(
    id='call_00_RVeTBjFqVOa65m2WEvmD7379', 
    function=Function(arguments='{"location": "Nanning, Guangxi"}', 
    name='get_weather'), 
    type='function', index=0
)], 
reasoning_content='The user wants weather in Nanning, Guangxi. Let me call the tool.')
'''
log.info(message);

# 3.把模型返回消息加进历史
messages.append(message)

# 4.取出它建议调用的工具
tool_call = message.tool_calls[0]
function_name = tool_call.function.name # 获取方法名 get_weather
arguments = json.loads(tool_call.function.arguments) # 获取方法参数 {"location": "Nanning, Guangxi"}

# 5.真正执行自己的函数
if function_name == "get_weather":
    # 这里是真实逻辑，例如调用天气API、查数据库等
    result = "24℃"
else:
    result = "未知工具"

# 6.把结果以 role="tool" 的形式发回
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,   # 必须和模型返回的 id 对应上
    "content": result               # 工具执行结果（字符串）
})

# 7.第二次调用模型，拿到最终答案
final_message = send_messages(messages)
log.info(final_message)
log.info(final_message.content)