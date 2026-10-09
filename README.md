# 个人Agent学习

一个根据openai-agents-python（OpenAI Agents SDK）中文教程的学习

## 目录情况

- `logging.conf` 日志打印配置文件
- `.env` 存储模型的key等信息（不提交）
- `requirements.txt` 存储学习过程中项目所需依赖
- `myjson.json` 一个json文件，便于格式化json
- utils
    - `logger.py` 日志打印工具类
    - `getagentkey.py` 由于使用deepseek作为模型，因此需要重写一些OpenAI原本封装好的属性，便于后续各个文件调用
    - `getclient.py` 封装client，便于后续调用
    - `getclient_ollama.py` 封装client，便于后续调用，用于调用本地ollama部署的模型
    - `constants.py` 放置常量
    - `json_utils.py` 格式化JSON的工具，用于打印日志，便于查看
    - `safe_eval.py` 自定义的安全eval表达式，防止直接通过操作系统
    - `my_function.py` 存储常用方法
    - `my_async_function.py` 存储异步常用方法
- toolcalling: tool calling的学习
    - `00-calling.py` 不使用tool直接调用模型
    - `01-create-tool.py` 定义第一个tool
    - `02-call-function.py` 程序执行tool
    - `03-input-append.py` 把 Tool Output 交还给模型
    - `04_try_ollama.py` 测试本地模型运行情况
- agentloop: Agent Loop的学习
    - `00-use-client-chat.py` 使用与原来`client.responses.create()`不同的请求，返回对象会不一致
    - `01-create-tool2.py` 使用`client.chat.completions.create`调用LLM，使LLM获取Tool并获取返回值
    - `02-first-agent-loop.py` Agent Loop第一版
- toolregistry: 多个tool的管理
    - `01-multiple-tool-calling.py` 管理多个`tool`，执行多个`tool calling`
- toolchoice: `toolchoice` 的学习
    - `01_tool_choice_test.py` 各个模式的区别
    - `02_tool_choice_function.py` 指定function模式
    - toolchoice_orders_demo: 小型的订单项目实战，系统学习tool choice
        - `tod01_main.py`
        - `tools.py`
        - `agent.py`
- toolexecution: 顺序执行与并行（Sequential / Parallel Tool Execution）
    - `01-sequential-demo.py` 进行代码的正常顺序执行
    - `02-sequential-async-await.py` 使用异步`async`、`await` 控制代码的顺序执行（仍为顺序执行，但是使用异步控制）
    - `03-asyncio-gather.py` 使用`asyncio.gather()`并行多个异步任务
    - `04_parallel_tool.py` 并行执行tool

---

## 知识点

| 名称            | 在本教程里的意思              | 由谁控制         |
| ------------- | --------------------- | ------------ |
| Tool Schema   | 给模型看的工具说明，写明名称、用途、参数  | 你写的程序        |
| Tool Call     | 模型提出“请调用这个函数并传这些参数”   | 模型生成，程序校验    |
| Tool Result   | Python 实际执行后返回的结果     | 你写的函数        |
| Agent Loop    | 反复请求模型、执行工具、回传结果，直到结束 | 你写的程序        |
| 工具注册表         | 把工具名、说明、Python 函数集中管理 | 你写的程序        |
| `tool_choice` | 规定模型能否或必须选择工具         | 请求参数，受模型支持约束 |

### Tool Calling

> JSON Schema

| 字段 | 作用 |
| ---- | ---- |
| type | 工具类型。Function Tool 使用 function。 |
| name | 模型调用时使用的函数名。 |
| description | 告诉模型什么时候应该使用这个工具。 |
| parameters | 描述工具参数的 JSON Schema。 |
| properties | 每个参数的定义。 |
| required | 哪些参数必须提供。 |
| additionalProperties | 通常在 strict 模式下设置为 false。 |
| strict | 让工具参数更加严格地遵循 Schema。 |

一个非常重要的思想：Tool Schema 就像给模型看的 API 接口文档。模型不是直接读取你的 Python 函数签名，而是根据你提供的工具定义生成调用参数。

#### 单个Tool call的执行流程

> 声明Python函数

```python
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
```

> 定义一个tool

```python
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
```

> 让模型产生tool call

```python
my_input = [
    {"role": "user", "content": "北京现在天气怎么样？"}
]

tools = [weather_tool]

response = client.responses.create(
    model=DEFAULT_MODEL,
    tools=tools,
    input=my_input
)
```
*注意！该步骤中只是让模型产生tool，但是模型只是提出调用请求，它没有执行Python 函数*

input/messages中的角色

|role |	谁说的 |	作用 |
| --- | --- | --- |
|system |	开发者 |	设定模型的身份、行为规范、约束 |
|user |	用户 |	用户输入的问题或指令 |
|assistant |	模型 |	模型之前的回复（包括纯文本和 tool_calls） |
|tool |	你的程序 |	工具执行结果，回传给模型 |

> 创建方法读取调用模型返回值

```python
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
```

> 执行自己定义的tool（与下方代码重复）

```python
for item in response.output:
    if item.type == "function_call":
        args = orjson.loads(item.arguments)
        result = call_function(item.name, args)
        log.info(f'工具结果: {result}')
```

*至此，程序完成：模型 → function_call → Python → get_weather() → result*

> 把Tool output交还模型

模型只会"说"它想调用哪个工具，它没有手。get_weather 是你在本地执行的，执行结果必须通过 input.append 喂回给模型，模型才能基于这个结果生成最终回答。这就是 Agent 从"模型提请求"到"给出答案"必经的一次往返，也是 ReAct 循环的核心。
```
        ┌─────────────────────────────┐
        │  用户输入 / 工具结果        │
        └──────────────┬──────────────┘
                       ↓
              ┌────────────────┐
              │  调用 LLM      │
              └────────┬───────┘
                       ↓
              ┌────────────────┐
              │ 模型输出是什么？│
              └────┬───────┬───┘
        要调工具    │       │  直接回答
                   ↓       ↓
          ┌────────────┐  ┌────────┐
          │ 本地执行工具│  │ 返回答案│
          └─────┬──────┘  └────────┘
                ↓
        ┌──────────────────┐
        │ 把结果追加到 input│
        └────────┬─────────┘
                 ↓
              （回到调用 LLM）
```
- 单次工具调用：循环 2 次（请求 → 执行 → 回答）
- 多步任务（比如"先查天气，再决定穿什么"）：循环可能 3 次、4 次……
- 模型直接回答（不需要工具）：循环 1 次就结束

```python
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
log.info(final_response.output_text) #  南宁现在天气**晴**，气温大约 **31°C**，比较炎热，出门注意防晒补水。☀️
```

*值得注意的是，在交还模型的过程中，记得使用`my_input.append(item)`追加function_call请求（不知道是不是deepseek的需求，GPT提供的文档没有这一步，导致了`Error code: 400 - {'error': {'message': 'No tool call found for tool output with call_id call_00_O6f4tl0zhNSnjrPAmoSb6262.', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_request_error'}}`异常，问了deepseek，回答是只追加了 function_call_output，却遗漏了与之配对的 function_call 本身。）*
*再次返回时，不会是冷冰冰的tool结果，而会添加模型的一些分析回答。至此，完成 用户 → 模型 → Tool Call → Python Tool → Tool Output → 模型 → 最终回答 闭环。*

---

### Agent Loop


> **LLM 不是真的在执行 Python 函数。**

例如我们定义：

```python
def get_weather(city: str):
    return {"city": city, "temperature": 25}
```

模型实际上不会直接执行：

```python
get_weather("上海")
```

真正发生的是：

```text
用户
 ↓
LLM
 ↓
LLM 返回：
“我要调用 get_weather，参数是 city=上海”
 ↓
你的 Python 程序
 ↓
真正执行 get_weather("上海")
 ↓
得到结果
 ↓
Python 把结果发送回 LLM
 ↓
LLM 根据工具结果生成最终回答
```

因此 Tool Calling 的本质可以概括为：

```text
LLM 负责决定“调用什么、参数是什么”
程序负责真正“执行什么”
```

而 **Agent Loop** 就是在 Tool Calling 的基础上增加一个循环：

```text
用户问题
   ↓
LLM
   ↓
是否需要 Tool？
 ┌─┴─────────────┐
 否              是
 ↓               ↓
最终回答      执行 Tool
                 ↓
             Tool Result
                 ↓
                LLM
                 ↓
          是否还需要 Tool？
           ┌─────┴─────┐
          否           是
          ↓            ↓
       最终回答      再执行 Tool
```

因此：

> **Agent Loop = LLM + Tool + Tool Result + 循环**

这也是理解 Agent 最重要的一步。

#### Agent Loop的简易执行流程

现在默认整个执行都在一个循环当中，在模型返回不再需要调用Tool前，都会一直调用Tool，直到模型判定不再需要调用为止

> 请求模型并获得请求结果

```python
response = client.chat.completions.create(
    model=DEEPSEEK_FLASH_MODEL,
    messages=messages,
    tools=tools,
)
message = response.choices[0].message
```

> 把 assistant 的响应加入历史

```python
messages.append(message)
```

*为什么必须把 assistant 的 tool_calls 放回 messages*

正确顺序如下：

```
user
 ↓
assistant + tool_calls
 ↓
tool
 ↓
assistant
```

例如

```python
messages = [
    {
        "role": "user",
        "content": "上海天气怎么样？"
    },

    {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "call_123",
                "function": {
                    "name": "get_weather",
                    "arguments": "{\"city\":\"上海\"}"
                }
            }
        ]
    },

    {
        "role": "tool",
        "tool_call_id": "call_123",
        "content": "{\"temperature\":28,\"weather\":\"多云\"}"
    }
]
```

*因为 `Tool Result`的`tool_call_id`必须对应`assistant`发出的`tool_calls的id`，模型需要知道【我之前要求做了什么？这个 tool result 对应哪个调用？】*
*assistant 的 tool_calls 和 tool result 是一对。*

```

> 没有 Tool Call，说明模型已经可以直接回答，并结束Agent Loop

```python
if not message.tool_calls:
    log.info(f"tool_calls已为空，可以输出结果：{message.content}")
    break
```

> 执行所有 Tool Call，并将结果返回给模型

```python
# 执行所有 Tool Call
for tool_call in message.tool_calls:
    tool_name = tool_call.function.name
    arguments = orjson.loads(tool_call.function.arguments)
    if tool_name == "get_weather":
        result = get_weather(arguments["city"])
    else:
        result = {"error": f"未知工具：{tool_name}"}
    # 将结果返回给模型
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": orjson.dumps(result).decode("utf-8")
    })
```

> LLM表达结束的方式

| 信号 | 含义 |
| --- | --- |
| message.tool_calls 为空 |	模型没有要求调用工具，直接给了文字回答 |
| finish_reason == "stop" |	模型正常说完了 |
| finish_reason == "tool_calls" | 模型要求调工具，循环要继续 |
| finish_reason == "length" | 输出被截断，属于异常情况 |

---

### Tool Registry

把模型看到的 `Tool` 和 `Python 真正执行的函数` 连接起来。

```
┌──────────────────────┐
│       LLM            │
└──────────┬───────────┘
           │
           │ tool name
           ↓
┌──────────────────────┐
│    TOOL_REGISTRY     │
│                      │
│ get_weather → fn     │
│ calculator  → fn     │
│ search      → fn     │
└──────────┬───────────┘
           │
           ↓
       Python Function
```

后续如需增加 Tool 只需要用代码即可调用：

```python
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_time": get_time,
    "calculator": calculator,
}

TOOL_REGISTRY["get_time"] = get_time
```

---

### Multiple Tool Calling

一次 `LLM Response` 返回多个 `Tool Call`。

例如：

```
用户：
南宁天气怎么样？现在几点？
```


模型可能返回：

```text
tool_calls:

1. get_weather({"city": "上海"})

2. get_time({"city": "上海"})
```

也就是：

```python
message.tool_calls = [
    tool_call_1,
    tool_call_2,
]
```

所以千万不要写：

```python
tool_call = message.tool_calls[0]
```

然后认为只有一个。更稳妥的方法是这样实现的：

```python
for tool_call in message.tool_calls:
    ...
```

#### Multiple Tool Calling 的完整执行过程

假设：

```text
User:
南宁天气怎么样？现在几点？
```

第一次：

```text
LLM
 ↓
返回两个 Tool Call

get_weather("南宁")
get_time("南宁")
```

Python：

```text
执行 get_weather
执行 get_time
```

得到：

```text
weather_result
time_result
```

然后：

```text
messages
 ↓
assistant tool_calls
 ↓
tool result 1
tool result 2
```

再次调用 LLM。

最终：

```text
南宁目前 30℃，天气多云，现在是 10:30。
```

#### 结合代码的具体流程

> 定义多个tool

```python
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
    return {
        "expression": expression,
        "result": eval(expression),
    }
```

> 注册tool（Registry）

```python
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_time": get_time,
    "calculator": calculator,
}
```

> 调用指定TOOL

```python
for tool_call in message.tool_calls:
    ...
    # 根据被管理的tool去调用
    function = TOOL_REGISTRY.get(tool_name)
    ...
```

---

### Tool Choice

`Tool Calling` 解决的是模型如何提出工具调用请求；而 `tool_choice` 解决的是这一轮模型到底能不能调用 Tool，以及应该以多大自由度选择 Tool？

``` text
tools
    ↓
有哪些 Tool

tool_choice
    ↓
这一轮怎么选 Tool

tool_calls
    ↓
模型最终实际选择了什么
```

#### 四种核心模式

DeepSeek Chat Completions 当前支持一下4种模式

| 写法 | 含义 |
| --- | --- |
| none | 禁止调用 Tool |
| auto | 模型自行决定是否调用 Tool |
| required | 必须调用一个或多个 Tool（当前deepseek思考模式下不支持） |
| 指定 function | 强制调用指定 Tool（当前deepseek思考模式下不支持） |

*思考模式可以通过`extra_body={"thinking": {"type": "enabled/disabled"}}`来进行控制*

> 基本代码

基本代码

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    tool_choice="none"
)

tool_choice="none"
tool_choice="auto"
tool_choice="required"
tool_choice={
    "type": "function",
    "function": {
        "name": "get_weather"
    }
}
```

> 模式对比

| 模式 | 能否不调用 Tool | 是否必须 Tool | 是否指定具体 Tool |
| --- | --- | --- | --- |
| none | ❌ | ❌ | ❌ |
| auto | ✅ | ❌ | ❌ |
| required | ❌ | ✅  | ❌ |
| specific function | ❌ | ✅  | ✅  |

 `tool_choice` 是 Agent Runtime 的一个**控制点**：

``` text
User
 ↓
LLM
 ↓
tool_choice
 ↓
┌───────────────┐
│ none          │ → 不调用
│ auto          │ → 模型决定
│ required      │ → 必须调用
│ specific      │ → 指定调用
└───────────────┘
 ↓
tool_calls
 ↓
Python Runtime
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

#### 一些小坑

1. 如果业务上根本不需要 Tool，强制调用反而会制造无意义调用。
2. 当前学习过程中，我只尝试了`deepseek`云端模型和`ollama`部署的`qwen3.5:4b`，通过`ollama`部署的模型并不能像`deepseek`一样使用`required`规定强制调用模型，这是当前`ollama`存在的问题，如果找不到必须调用的方法，它会默认使用`auto`。
3. `Ollama`静默忽略`tool_choice`。

---

### 顺序调用与并行调用（Sequential / Parallel Tool Execution）

模型一次返回多个 Tool Call，不等于 Python 必须并行执行这些 Tool。

```
多个 Tool
   ↓
应该一个一个执行？
还是
应该同时执行？
```

> 关键流程

``` text
Multiple Tool Calling
        ≠
Parallel Tool Execution
```

完整关系是：

``` text
              LLM
               ↓
       一次产生多个 Tool Call
               ↓
          Python Runtime
               ↓
       ┌───────┴───────┐
       ↓               ↓
    Sequential       Parallel
       ↓               ↓
      for          asyncio.gather
```

也就是说：

> **LLM 决定"要调用什么"，你的程序决定"怎么执行"。**

DeepSeek 官方文档也明确说明 Tool Calls 可以支持多个函数调用，并支持
parallel function calls；Chat Completions 中 `tool_choice="auto"`
可以让模型选择调用一个或多个工具。

> 为何要并行？

假设三个 Tool：

``` text
天气 API       2 秒
时间 API       1 秒
汇率 API       3 秒
```

顺序：

``` text
2 + 1 + 3 = 6 秒
```

并行：

``` text
max(2, 1, 3) = 3 秒
```

图示：

``` text
顺序：

Weather  ─────2s─────>
                       Time ─1s─>
                              Exchange ─────3s─────>

总耗时 ≈ 6 秒
```

并行：

``` text
Weather  ─────2s─────────>
Time     ─1s─────────────>
Exchange ───────3s───────>

总耗时 ≈ 3 秒
```

真实系统还会受到网络、API 限流、连接池等因素影响，但核心思想不变：

> **独立的 I/O 操作可以并发等待。**

#### Sequential

> 程序本身的顺序执行

由于程序是逐行执行，因此在不使用`async`等关键字控制时，代码自行会顺序执行。

> 使用`async`-`await`控制顺序执行

把 Tool 改成异步函数：

``` python
import asyncio


async def get_weather(city: str):

    print(f"开始查询 {city} 天气")

    await asyncio.sleep(2)

    return {
        "city": city,
        "temperature": 28,
        "weather": "晴",
    }


async def get_time(city: str):

    print(f"开始查询 {city} 时间")

    await asyncio.sleep(1)

    return {
        "city": city,
        "time": "10:30",
    }
```

这里：

``` python
async def
```

定义异步函数。

而：

``` python
await
```

表示等待一个异步操作。

*`async` 不等于并行。*

> asyncio.run()

asyncio.run() 的作用是：启动一个异步事件循环，运行传入的协程，等它执行完，然后关闭事件循环。它是同步代码进入异步世界的入口。

Python 的 async def 函数调用后不会立刻执行，而是返回一个协程对象：

```python
async def hello():
    return "hi"

coro = hello()          # 只是创建协程，没执行
print(coro)             # <coroutine object hello at 0x...>
print(hello())          # 还会提示 "coroutine was never awaited"
```

必须交给事件循环调度才会真正跑起来，asyncio.run() 就是最省事的调度方式：

```python
result = asyncio.run(hello())
print(result)   # "hi"
```

#### Parallel

可以使用`asyncio.gather()`并行多个异步任务

```python
weather, current_time = await asyncio.gather(
    get_weather("上海"),
    get_time("南宁")
)
```

> gather 的核心思想

``` python
await asyncio.gather(
    task_a(),
    task_b(),
    task_c(),
)
```

可以理解为：

``` text
       ┌→ task A
       │
开始 ──┼→ task B
       │
       └→ task C
              ↓
          等待全部完成
              ↓
             results
```

> gather 的返回顺序

假设：

``` python
results = await asyncio.gather(
    slow_task(),
    fast_task(),
)
```

即使：

``` text
fast_task
```

先完成：

``` text
fast → 完成
slow → 完成
```

返回结果仍然对应传入顺序：

``` python
results[0]  # slow_task
results[1]  # fast_task
```

所以在 Agent 中不要只依赖列表位置。

最好保留：

``` python
tool_call_id
```

#### 异步 Tool Registry的流程

```
LLM
 ↓
产生多个 Tool Call
 ↓
Python 并行执行
 ↓
把结果全部交给 LLM
 ↓
LLM 再继续
```

`Parallel Tool Execution` 本质上是 Agent Runtime 层面的并发优化