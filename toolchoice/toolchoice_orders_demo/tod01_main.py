from toolchoice.toolchoice_orders_demo.agent import run_agent
from utils.logger import log

def test_run_agent(user_input: str, tool_choice: str="auto"):
    if tool_choice == "auto":
        return run_agent(user_input)
    if tool_choice == "required":
        return run_agent(user_input, tool_choice)
    else:
        return run_agent(user_input, "none")

if __name__ == "__main__":
    answer = test_run_agent("你好，帮我查询订单10001状态", "auto")
    # tool_choice = {
    #     "type": "function",
    #     "function": {
    #         "name": "get_order"
    #     }
    # }
    # answer = run_agent("你好，帮我查询订单10001状态", tool_choice)
    log.info(f"answer - {answer}")