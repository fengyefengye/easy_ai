from __future__ import annotations

import json
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


def _parse_mcp_servers(mcp_servers_json: str) -> dict[str, MCPConnection]:
    if not mcp_servers_json:
        return {}
    parsed = json.loads(mcp_servers_json)
    if not isinstance(parsed, dict):
        raise ValueError("MCP_SERVERS_JSON 必须是对象类型JSON")
    return cast(dict[str, MCPConnection], parsed)


async def load_mcp_tools(mcp_servers_json: str) -> list[BaseTool]:
    connections = _parse_mcp_servers(mcp_servers_json)
    if not connections:
        return []
    client = MultiServerMCPClient(connections)
    return await client.get_tools()
