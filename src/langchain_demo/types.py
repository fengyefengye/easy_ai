from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToolCallRecord:
    id: str
    name: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntermediateOutput:
    type: str
    content: str
    tool_name: str | None = None
    tool_call_id: str | None = None


@dataclass
class ChatResponse:
    answer: str
    intermediate_outputs: list[IntermediateOutput] = field(default_factory=list)
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    workflow: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """将响应对象转换为可 JSON 序列化的字典。"""
        return asdict(self)
