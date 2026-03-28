from __future__ import annotations

from langchain_demo.agent import AgentService, get_builtin_tools, load_mcp_tools
from langchain_demo.chains import build_qa_chain
from langchain_demo.config import load_settings
from langchain_demo.llm import create_chat_model
from langchain_demo.services import ChatService
from langchain_demo.types import ChatResponse


def run(question: str) -> ChatResponse:
    """执行基础 QA 链路并返回统一响应结构。"""
    settings = load_settings()
    model = create_chat_model(settings)
    chain = build_qa_chain(model)
    chat_service = ChatService(chain)
    return chat_service.ask(question)


async def run_agent(question: str, enable_mcp: bool) -> ChatResponse:
    """执行 Agent 链路，可选加载 MCP 工具。"""
    settings = load_settings()
    model = create_chat_model(settings)
    tools = get_builtin_tools()
    mcp_warning: str | None = None
    if enable_mcp:
        try:
            tools.extend(await load_mcp_tools(settings.mcp_servers_file))
        except Exception as exc:
            mcp_warning = (
                "MCP 工具加载失败，已降级为仅使用内置工具。"
                f" 原始错误: {exc}"
            )
    agent_service = AgentService(
        model=model,
        tools=tools,
        system_prompt=settings.agent_system_prompt,
    )
    response = await agent_service.ask(question)
    if mcp_warning is not None:
        response.workflow["mcp_warning"] = mcp_warning
    return response
