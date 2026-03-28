from __future__ import annotations

import ast
from pathlib import Path
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


def _resolve_optional_extension_path(project_root: Path, raw_path: str) -> tuple[Path | None, str | None]:
    """当路径未带扩展名时，尝试在同目录按文件 stem 匹配真实文件。"""
    requested = Path(raw_path)
    if requested.suffix:
        return None, None

    requested_parent = requested.parent if str(requested.parent) != "." else Path("")
    search_dir = (project_root / requested_parent).resolve()
    if project_root not in search_dir.parents and search_dir != project_root:
        return None, None
    if not search_dir.exists() or not search_dir.is_dir():
        return None, None

    stem_name = requested.name.casefold()
    matches = [
        candidate.resolve()
        for candidate in search_dir.iterdir()
        if candidate.is_file() and candidate.stem.casefold() == stem_name
    ]
    if not matches:
        return None, None
    matches.sort(key=lambda item: (item.suffix.lower() != ".md", item.name.lower()))
    if len(matches) == 1:
        return matches[0], None

    match_names = ", ".join(match.name for match in matches[:5])
    return None, f"文件名不唯一，请指定扩展名。可选: {match_names}"


def _eval_expr(node: ast.AST) -> float:
    """递归计算 AST 表达式节点，仅允许安全算术运算。"""
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


@tool
def read_file_head(path: str, max_lines: int = 10) -> str:
    """只读方式读取文件前 N 行，路径限制在当前项目目录内。"""
    project_root = Path.cwd().resolve()
    target = Path(path)
    if not target.is_absolute():
        target = (project_root / target).resolve()
    else:
        target = target.resolve()
    if project_root not in target.parents and target != project_root:
        return f"拒绝访问: 仅允许读取项目目录内文件。project_root={project_root}"
    if not target.exists():
        fallback_target, fallback_error = _resolve_optional_extension_path(project_root, path)
        if fallback_target is not None:
            target = fallback_target
        elif fallback_error is not None:
            return fallback_error
        else:
            return f"文件不存在: {target}"
    if not target.is_file():
        return f"目标不是文件: {target}"
    safe_max_lines = min(max(max_lines, 1), 200)
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    head = lines[:safe_max_lines]
    return "\n".join(head)


def get_builtin_tools() -> list[BaseTool]:
    """返回内置工具列表。"""
    return [calculator, current_time, read_file_head]
