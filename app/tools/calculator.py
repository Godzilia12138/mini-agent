import ast
import operator

from app.tools.base import Tool

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_expr(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_expr(node.operand))
    raise ValueError("不支持的表达式")


class CalculatorTool(Tool):
    name = "calculator"
    description = "计算数学表达式，支持 + - * / // % ** 和括号"
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "数学表达式，如 (1 + 2) * 3",
            },
        },
        "required": ["expression"],
    }

    def execute(self, args: dict) -> str:
        expr = args.get("expression", "").strip()
        if not expr:
            return "请提供表达式"
        try:
            tree = ast.parse(expr, mode="eval")
            result = _eval_expr(tree.body)
            if isinstance(result, float) and result == int(result):
                result = int(result)
            return str(result)
        except Exception as e:
            return f"计算失败: {e}"
