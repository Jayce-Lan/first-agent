# 个人Agent学习

一个根据openai-agents-python（OpenAI Agents SDK）中文教程的学习

## 目录情况

- `logging.conf` 日志打印配置文件
- `anser.md` 存储一些ai问题的解答
- `.env` 存储模型的key等信息（不提交）
- `requirements.txt` 存储学习过程中项目所需依赖
- `myjson.json` 一个json文件，便于格式化json
- utils
    - `logger.py` 日志打印工具类
    - `getagentkey.py` 由于使用deepseek作为模型，因此需要重写一些OpenAI原本封装好的属性，便于后续各个文件调用
    - `getclient.py` 封装client，便于后续调用
    - `constants.py` 放置常量
- toolcalling: tool calling的学习
    - `00-calling.py` 不使用tool直接调用模型
    - `01-create-tool.py` 定义第一个tool
    - `02-call-function.py` 程序执行tool
    - `03-input-append.py` 把 Tool Output 交还给模型
- agentloop: Agent Loop的学习
    - `00-use-client-chat.py` 使用与原来`client.responses.create()`不同的请求，返回对象会不一致
    - `01-minimal-loop.py` 完整最小Agent Loop

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

**Agent Loop（智能体循环）** 是 AI Agent 的核心运行机制：它让模型不是只做一次“输入→输出”，而是围绕一个目标不断重复 **观察 → 思考/规划 → 行动 → 获取反馈 → 更新状态**，直到任务完成或触发终止条件。也就是常说的 ReAct 循环：推理、行动、观察，再推理。

> 普通 LLM 调用通常是：

输入 → 模型生成 → 输出

> Agent Loop 则是：

输入 → 多轮推理 → 调用工具 → 读取结果 → 调整计划 → 再行动 → 输出

它让 LLM 从“一次性文本生成器”变成能多步执行、试错和利用外部信息的“自主执行器”。

```text
用户提出问题
    ↓
Python 发出请求：messages + tools + tool_choice
    ↓
模型返回普通回答，或返回一个/多个 tool_calls
    ↓ 若返回 tool_calls
Python 根据工具名找到已注册函数 → 校验参数 → 执行函数
    ↓
把 assistant 的调用消息和每条 tool 结果追加到 messages
    ↓
再次请求模型；重复，直至普通回答或达到限制
```

OpenAI 官方把这个过程归纳为五步：提供工具、收到调用、应用程序执行、把结果发回模型、获得答案或更多调用。**Agent Loop 就是重复后面几步的 Python 控制循环**，不是让模型获得直接执行 Python 的权限。参见 [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling/)。

> 按执行顺序解读`01-minimal-loop.py`这段代码：

1. `messages` 初始只有系统说明和用户提问。它是这次任务的“对话本”。DeepSeek 的多轮 Chat Completions 需要程序自行管理并再次传入历史消息。参见 DeepSeek Multi-round Conversation。
2. 每进一次 for，就向模型发出一次请求。max_rounds=5 限制模型请求轮数，避免反复调用不结束。
3. `assistant_message.tool_calls or []`：没有调用时得到空列表；有调用时可能有一条，也可能有多条。
4. `finish_reason="length"` 可能意味着生成被截断，这时不要执行不完整的 JSON。tool_calls 通常表示模型提出工具调用，stop 通常表示生成结束；仍要检查实际的 message.tool_calls。其他非正常停止原因交由程序处理。参见 DeepSeek API 参考。
5. `if not calls`：这轮模型不再要工具，返回文本，循环完成。
6. `messages.append(assistant_message.model_dump(...))`：保存模型提出工具调用的原消息。不能只保存工具执行结果，否则下一轮模型看不到自己刚提出的调用。
7. `orjson.loads(...)`：把模型返回的参数 JSON 字符串转成 Python 字典。模型产出的内容都要校验，所以检查字段集合、类型和值。
8. `tool_call_id=call.id`：工具结果必须对应具体的调用 ID。它不是工具名。json.dumps(..., ensure_ascii=False) 把字典变为结果消息需要的字符串，并保持中文可读。
9. `except`：参数错误也返回结构化错误，使模型知道工具没成功；不把未经校验的参数直接传给业务函数。

试运行：`01-minimal-loop.py`。模型可能在第一轮同时请求北京、新加坡两个天气，也可能先请求一个再请求另一个。两种都属于正常行为。