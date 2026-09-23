'''
    首个智能体
'''

import asyncio
from utils.logger import log
from utils.getagentkey import myModel
from agents import Agent, Runner

# 智能体由 instructions、名称以及特定模型等可选配置定义。
agent = Agent(
    name="History Tutor",
    instructions="You answer history questions clearly and concisely.",
    model=myModel
)

# 使用 Runner 执行智能体，并获取返回的 RunResult。
async def main():
    result = await Runner.run(agent, "When did the Roman Empire fall?")
    log.info(result)

if __name__ == "__main__":
    asyncio.run(main())
