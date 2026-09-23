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
- chapt0demo
    - `deepseekhello.py` 类似于hello world，了解tool-calls
    - `helloworld.py` 关于tool-calls的详细工作流程
- deepseekapi
    - `tool-call.py` 关于tool-calls的详细工作流程
- agentssdk
    - `00-helloworld.py` 使用`openai-agents` 完成Hello world 示例
    - `01-first-agent-runner.py` 首个智能体运行
- toolcalling
    - `00-calling.py` 不使用tool直接调用模型
    - `01-create-tool.py` 定义第一个tool

## 知识点

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