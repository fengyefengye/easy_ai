from __future__ import annotations

from langchain_core.runnables import Runnable

from langchain_demo.types import ChatResponse, IntermediateOutput


class ChatService:
    def __init__(self, chain: Runnable[dict[str, str], str]) -> None:
        """注入问答链路。"""
        self._chain = chain

    def ask(self, question: str) -> ChatResponse:
        """执行问答链并封装为统一响应结构。"""
        try:
            answer = self._chain.invoke({"question": question})
        except Exception as exc:
            error_message = f"模型调用失败: {exc}"
            return ChatResponse(
                answer=error_message,
                workflow={
                    "invoke_input_messages": [{"role": "user", "content": question}],
                    "conversation": [],
                    "final_result": error_message,
                    "error": str(exc),
                },
            )
        return ChatResponse(
            answer=answer,
            intermediate_outputs=[IntermediateOutput(type="ai", content=answer)],
            workflow={
                "invoke_input_messages": [{"role": "user", "content": question}],
                "conversation": [{"type": "ai_output", "content": answer}],
                "final_result": answer,
            },
        )
