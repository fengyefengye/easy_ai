from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI


def build_qa_chain(model: ChatOpenAI) -> Runnable[dict[str, str], str]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个严谨的AI助手。请先给出核心结论，再补充最多十条简洁要点。",
            ),
            ("human", "问题：{question}"),
        ]
    )
    return prompt | model | StrOutputParser()
