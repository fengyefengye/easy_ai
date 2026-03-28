from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    api_key: str
    base_url: str
    model: str
    temperature: float
    agent_system_prompt: str
    mcp_servers_file: str


def _config_dir() -> Path:
    """返回配置目录路径。"""
    return Path(__file__).resolve().parent


def _load_dotenv_file() -> None:
    """从配置目录 `.env` 加载环境变量（不覆盖已存在变量）。"""
    dotenv_path = _config_dir() / ".env"
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def load_settings() -> AppSettings:
    """从环境变量与 `.env` 文件组装应用配置。"""
    _load_dotenv_file()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required")

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
    temperature_raw = os.getenv("LLM_TEMPERATURE", "0.2").strip()
    temperature = float(temperature_raw)
    agent_system_prompt = os.getenv(
        "AGENT_SYSTEM_PROMPT",
        "你是一个严谨的智能体助手。优先使用工具来获取事实，结论简洁准确。",
    ).strip()
    mcp_servers_file = str(_config_dir() / "mcp_servers.json")

    return AppSettings(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        agent_system_prompt=agent_system_prompt,
        mcp_servers_file=mcp_servers_file,
    )
