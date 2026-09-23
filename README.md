# 个人Agent学习

一个根据openai-agents-python（OpenAI Agents SDK）中文教程的学习

## 目录情况

- `logging.conf` 日志打印配置文件
- `anser.md` 存储一些ai问题的解答
- `.env` 存储模型的key等信息（不提交）
- `requirements.txt` 存储学习过程中项目所需依赖
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
    - `00-calling.py` 
