from __future__ import annotations

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from langchain_demo.config import AppSettings


def create_chat_model(settings: AppSettings) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=SecretStr(settings.api_key),
        base_url=settings.base_url,
        model=settings.model,
        temperature=settings.temperature,
    )
