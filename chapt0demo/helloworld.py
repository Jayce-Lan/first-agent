import os
import ast
import json
import operator
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 读取 .env 里的配置
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# ============ 1. 给 Agent 一双"手"（工具） ============

def get_weather(city: str) -> str:
    """查天气工具"""
    # 真实项目这里应该调用天气 API，我们先用模拟数据
    return f"{city}今天天气：晴，气温 25°C，适合出门！"

# 安全求值：禁止 eval() 直接执行用户输入！
# 只用 AST 白名单解析"数字 + 四则运算"，恶意表达式（如 __import__）会被拒绝
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}

def _safe_eval(node):
    """递归解析 AST 节点，只放行数字与四则运算"""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"不支持的表达式元素: {type(node).__name__}")

def calculator(expression: str) -> float:
    """计算器工具（只支持数字与 + - * / 等基础运算）"""
    return _safe_eval(ast.parse(expression, mode="eval"))

# 把工具"告诉"模型，让它知道能用什么
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气情况",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算，比如 (1+2)*3",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]

# ============ 2. 给 Agent 一个"大脑"（LLM） ============

client = OpenAI()  # 会自动读取 .env 里的 key

def run_agent(user_input: str) -> str:
    """运行 Agent：思考 → 调用工具 → 给出答案"""
    messages = [{"role": "user", "content": user_input}]

    # 第一次调用：让模型决定是否需要工具
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=TOOLS,
    )

    msg = response.choices[0].message

    # 如果模型想调用工具
    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"🛠️ 正在调用工具: {name}({args})")

            # 执行对应的工具函数
            if name == "get_weather":
                result = get_weather(args["city"])
            elif name == "calculator":
                result = calculator(args["expression"])
            else:
                result = "未知工具"

            # 把工具结果返回给模型
            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

        # 第二次调用：让模型基于工具结果生成最终回答
        final = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
        )
        return final.choices[0].message.content

    return msg.content

# ============ 3. 跟你的 Agent 聊天吧！ ============

if __name__ == "__main__":
    print("🤖 你的第一个 AI Agent 已上线！")
    print("=" * 50)

    test_questions = [
        "北京今天天气怎么样？",
        "帮我算一下 (123 + 456) * 2 等于多少？",
    ]

    for q in test_questions:
        print(f"\n🙋 你问：{q}")
        answer = run_agent(q)
        print(f"🤖 Agent 答：{answer}")