from __future__ import annotations

from collections.abc import Sequence

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI


def _extract_text(messages: Sequence[BaseMessage]) -> str:
    for message in reversed(messages):
        if not isinstance(message, AIMessage):
            continue
        if isinstance(message.content, str):
            return message.content
        if isinstance(message.content, list):
            parts: list[str] = []
            for part in message.content:
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text)
            if parts:
                return "\n".join(parts)
    return ""


class AgentService:
    def __init__(
        self,
        model: ChatOpenAI,
        tools: Sequence[BaseTool],
        system_prompt: str,
    ) -> None:
        self._agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
        )

    def ask(self, question: str) -> str:
        response = self._agent.invoke({"messages": [{"role": "user", "content": question}]})
        if not isinstance(response, dict):
            return str(response)
        messages = response.get("messages")
        if not isinstance(messages, list):
            return str(response)
        return _extract_text(messages) or str(response)
