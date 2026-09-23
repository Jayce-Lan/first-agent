from agents import Agent, Runner
from utils.logger import log
from utils.getagentkey import myModel

# 由于使用deepseek作为接入模型，因此需要自定义model
agent = Agent(
    name="Assistant", 
    instructions="You are a helpful assistant", 
    model=myModel
)

result = Runner.run_sync(agent, "写一段关于广西南宁的描述")
log.info(result)