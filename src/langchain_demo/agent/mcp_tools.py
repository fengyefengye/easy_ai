from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import (
    SSEConnection,
    StdioConnection,
    StreamableHttpConnection,
    WebsocketConnection,
)

MCPConnection = StdioConnection | SSEConnection | StreamableHttpConnection | WebsocketConnection

_READ_ONLY_BLOCKED_KEYWORDS = (
    "write",
    "edit",
    "create",
    "update",
    "delete",
    "remove",
    "rename",
    "move",
    "mkdir",
    "rmdir",
    "rm",
    "put",
    "post",
    "patch",
    "commit",
    "push",
    "checkout",
    "merge",
    "rebase",
    "reset",
    "stage",
    "unstage",
)


def _parse_mcp_servers(mcp_servers_file: str) -> dict[str, MCPConnection]:
    """从本地 JSON 配置文件解析 MCP 连接配置。"""
    config_path = Path(mcp_servers_file)
    if not config_path.exists():
        return {}
    parsed = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("MCP 配置文件内容必须是对象类型JSON")
    return cast(dict[str, MCPConnection], parsed)


def _is_read_only_tool(tool: BaseTool) -> bool:
    """判断工具名是否可视为只读操作。"""
    name = tool.name.lower()
    return not any(keyword in name for keyword in _READ_ONLY_BLOCKED_KEYWORDS)


def _filter_read_only_tools(tools: list[BaseTool]) -> list[BaseTool]:
    """过滤掉潜在写操作工具，仅保留只读工具。"""
    return [tool for tool in tools if _is_read_only_tool(tool)]


async def load_mcp_tools(mcp_servers_file: str) -> list[BaseTool]:
    """按文件配置创建 MCP 客户端并加载只读 MCP 工具。"""
    connections = _parse_mcp_servers(mcp_servers_file)
    if not connections:
        return []
    loaded_tools: list[BaseTool] = []
    errors: list[str] = []
    for server_name, connection in connections.items():
        client = MultiServerMCPClient({server_name: connection})
        try:
            tools = await client.get_tools()
        except Exception as exc:
            errors.append(f"{server_name}: {exc}")
            continue
        loaded_tools.extend(tools)
    if loaded_tools:
        return _filter_read_only_tools(loaded_tools)
    if errors:
        raise ValueError("所有 MCP 服务加载失败: " + "; ".join(errors))
    return []
