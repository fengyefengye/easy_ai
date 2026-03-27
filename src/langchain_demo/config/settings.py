from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    api_key: str
    base_url: str
    model: str
    temperature: float
    agent_system_prompt: str
    mcp_servers_json: str


def load_settings() -> AppSettings:
    api_key = os.getenv(
        "OPENAI_API_KEY",
        "sk-Fu27h1Sm3d4COOwC6ejz9t8f0KRSt2wjDXTAEB7yyRTZkXdo",
    ).strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required")

    base_url = os.getenv("OPENAI_BASE_URL", "https://chatapi.zjt66.top/v1").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
    temperature_raw = os.getenv("LLM_TEMPERATURE", "0.2").strip()
    temperature = float(temperature_raw)
    agent_system_prompt = os.getenv(
        "AGENT_SYSTEM_PROMPT",
        "你是一个严谨的智能体助手。优先使用工具来获取事实，结论简洁准确。",
    ).strip()
    mcp_servers_json = os.getenv("MCP_SERVERS_JSON", "").strip()

    return AppSettings(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        agent_system_prompt=agent_system_prompt,
        mcp_servers_json=mcp_servers_json,
    )
