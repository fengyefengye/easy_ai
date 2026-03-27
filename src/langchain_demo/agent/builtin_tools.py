from __future__ import annotations

import ast
from datetime import datetime, timezone
from typing import Any

from langchain_core.tools import BaseTool, tool

_BIN_OPS: dict[type[ast.operator], Any] = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a**b,
    ast.Mod: lambda a, b: a % b,
}

_UNARY_OPS: dict[type[ast.unaryop], Any] = {
    ast.UAdd: lambda a: +a,
    ast.USub: lambda a: -a,
}


def _eval_expr(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ValueError("不支持的运算符")
        return float(op(_eval_expr(node.left), _eval_expr(node.right)))
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError("不支持的一元运算")
        return float(op(_eval_expr(node.operand)))
    raise ValueError("表达式仅支持数字与算术运算")


@tool
def calculator(expression: str) -> str:
    """执行安全算术计算，支持 + - * / % ** 与括号。"""
    try:
        parsed = ast.parse(expression, mode="eval")
        value = _eval_expr(parsed.body)
    except Exception as exc:
        return f"计算失败: {exc}"
    if value.is_integer():
        return str(int(value))
    return str(value)


@tool
def current_time() -> str:
    """返回当前UTC时间（ISO 8601格式）。"""
    return datetime.now(tz=timezone.utc).isoformat()


def get_builtin_tools() -> list[BaseTool]:
    return [calculator, current_time]
