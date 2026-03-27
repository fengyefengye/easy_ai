from __future__ import annotations

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from langchain_demo.config import AppSettings


def create_chat_model(settings: AppSettings) -> ChatOpenAI:
    """基于应用配置创建 ChatOpenAI 客户端。"""
    return ChatOpenAI(
        api_key=SecretStr(settings.api_key),
        base_url=settings.base_url,
        model=settings.model,
        temperature=settings.temperature,
    )
