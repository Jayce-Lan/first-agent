import asyncio

from utils.logger import log

async def slow_tool():
    log.info("slow_tool: 开始执行慢速工具")
    await asyncio.sleep(10)
    log.info("slow_tool: 执行完成")
    return "慢速工具执行完成"

async def main():
    try:
        # 设置超时时间为5秒
        result = await asyncio.wait_for(
            slow_tool(), 
            timeout=2
        )
        log.info(f"工具执行结果: {result}")
    except asyncio.TimeoutError:
        log.error("工具执行超时，已取消执行")

asyncio.run(main())