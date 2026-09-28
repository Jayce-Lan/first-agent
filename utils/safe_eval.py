'''
    自定义的安全eval表达式，防止直接通过操作系统
'''
import ast, operator

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,      # 负号，如 -3
    ast.UAdd: operator.pos,      # 正号，如 +3
}

_MAX_DEPTH = 50   # 防止恶意深度嵌套


def _safe_eval(node, depth: int = 0):
    """递归解析 AST 节点，只放行数字与四则运算。

    Args:
        node: AST 节点。
        depth: 当前递归深度，用于防止无限嵌套。

    Returns:
        计算结果。

    Raises:
        ValueError: 表达式包含不支持的语法或运算符。
    """
    if depth > _MAX_DEPTH:
        raise ValueError("表达式嵌套过深")

    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, depth + 1)

    # 数字字面量（bool 是 int 的子类，这里显式排除）
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            raise ValueError("不支持布尔值")
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"不支持的常量类型: {type(node.value).__name__}")

    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        left = _safe_eval(node.left, depth + 1)
        right = _safe_eval(node.right, depth + 1)
        try:
            return _SAFE_OPS[type(node.op)](left, right)
        except ZeroDivisionError:
            raise ValueError("除数不能为 0") from None

    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand, depth + 1))

    raise ValueError(f"不支持的表达式: {type(node).__name__}")


def safe_eval(expression):
    """安全求值：接受字符串或已解析的 AST 节点。

    Args:
        expression: 数学表达式字符串，如 "(1+2)*3"，或 ast 节点。

    Returns:
        计算结果（int 或 float）。

    Raises:
        ValueError: 表达式非法或不支持。
    """
    if isinstance(expression, ast.AST):
        node = expression
    elif isinstance(expression, str):
        expr = expression.strip()
        if not expr:
            raise ValueError("表达式不能为空")
        try:
            node = ast.parse(expr, mode="eval")
        except SyntaxError as exc:
            raise ValueError(f"表达式语法错误: {exc.msg}") from None
    else:
        raise ValueError(f"不支持的输入类型: {type(expression).__name__}")

    return _safe_eval(node)