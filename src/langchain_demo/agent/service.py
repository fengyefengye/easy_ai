from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from langchain_demo.types import ChatResponse, IntermediateOutput, ToolCallRecord


def _extract_text(content: Any) -> str:
    """从消息 content 中提取可读文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict):
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text)
            elif isinstance(part, str) and part.strip():
                parts.append(part)
        return "\n".join(parts)
    return ""


def _extract_final_answer(messages: Sequence[BaseMessage]) -> str:
    """从消息序列中提取最后一个 AI 文本作为最终答案。"""
    for message in reversed(messages):
        if not isinstance(message, AIMessage):
            continue
        text = _extract_text(message.content)
        if text:
            return text
    return ""


class AgentService:
    def __init__(
        self,
        model: ChatOpenAI,
        tools: Sequence[BaseTool],
        system_prompt: str,
    ) -> None:
        """初始化 LangChain Agent 实例。"""
        self._tool_names = [tool.name for tool in tools]
        self._system_prompt = system_prompt
        self._model_name = str(getattr(model, "model_name", getattr(model, "model", "unknown")))
        self._agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
        )

    def ask(self, question: str) -> ChatResponse:
        """执行一次提问，并返回答案/中间输出/工具调用记录。"""
        invoke_messages = [{"role": "user", "content": question}]
        response = self._agent.invoke({"messages": invoke_messages})
        if not isinstance(response, dict):
            return ChatResponse(
                answer=str(response),
                workflow={
                    "agent_init": {
                        "model": self._model_name,
                        "system_prompt": self._system_prompt,
                        "tools": self._tool_names,
                    },
                    "invoke_input_messages": invoke_messages,
                    "conversation": [],
                    "final_result": str(response),
                },
            )
        messages = response.get("messages")
        if not isinstance(messages, list):
            return ChatResponse(
                answer=str(response),
                workflow={
                    "agent_init": {
                        "model": self._model_name,
                        "system_prompt": self._system_prompt,
                        "tools": self._tool_names,
                    },
                    "invoke_input_messages": invoke_messages,
                    "conversation": [],
                    "final_result": str(response),
                },
            )

        tool_calls: list[ToolCallRecord] = []
        intermediate_outputs: list[IntermediateOutput] = []
        conversation: list[dict[str, Any]] = []

        for message in messages:
            if isinstance(message, AIMessage):
                text = _extract_text(message.content)
                if text:
                    intermediate_outputs.append(IntermediateOutput(type="ai", content=text))
                    conversation.append(
                        {
                            "type": "ai_output",
                            "content": text,
                        }
                    )
                raw_tool_calls = getattr(message, "tool_calls", None)
                if isinstance(raw_tool_calls, list):
                    for call in raw_tool_calls:
                        if not isinstance(call, dict):
                            continue
                        call_id = call.get("id")
                        name = call.get("name")
                        args = call.get("args")
                        if isinstance(call_id, str) and isinstance(name, str):
                            args_dict = args if isinstance(args, dict) else {}
                            tool_calls.append(
                                ToolCallRecord(
                                    id=call_id,
                                    name=name,
                                    args=args_dict,
                                )
                            )
                            intermediate_outputs.append(
                                IntermediateOutput(
                                    type="ai_tool_call",
                                    content=json.dumps(args_dict, ensure_ascii=False),
                                    tool_name=name,
                                    tool_call_id=call_id,
                                )
                            )
                            conversation.append(
                                {
                                    "type": "ai_tool_call",
                                    "tool_name": name,
                                    "tool_call_id": call_id,
                                    "args": args_dict,
                                }
                            )
            elif isinstance(message, ToolMessage):
                tool_content = _extract_text(message.content)
                intermediate_outputs.append(
                    IntermediateOutput(
                        type="tool",
                        content=tool_content,
                        tool_name=message.name,
                        tool_call_id=message.tool_call_id,
                    )
                )
                conversation.append(
                    {
                        "type": "tool_output",
                        "tool_name": message.name,
                        "tool_call_id": message.tool_call_id,
                        "content": tool_content,
                    }
                )

        answer = _extract_final_answer(messages) or str(response)
        return ChatResponse(
            answer=answer,
            intermediate_outputs=intermediate_outputs,
            tool_calls=tool_calls,
            workflow={
                "agent_init": {
                    "model": self._model_name,
                    "system_prompt": self._system_prompt,
                    "tools": self._tool_names,
                },
                "invoke_input_messages": invoke_messages,
                "conversation": conversation,
                "final_result": answer,
            },
        )
