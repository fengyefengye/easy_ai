from __future__ import annotations

from langchain_core.runnables import Runnable


class ChatService:
    def __init__(self, chain: Runnable[dict[str, str], str]) -> None:
        self._chain = chain

    def ask(self, question: str) -> str:
        return self._chain.invoke({"question": question})
