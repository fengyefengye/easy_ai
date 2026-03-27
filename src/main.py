from __future__ import annotations

import argparse
import asyncio

from langchain_demo import run, run_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LangChain layered architecture demo")
    parser.add_argument("question", type=str, help="Question for the LLM")
    parser.add_argument(
        "--mode",
        choices=["qa", "agent"],
        default="agent",
        help="qa为基础问答链路，agent为工具调用智能体",
    )
    parser.add_argument(
        "--enable-mcp",
        action="store_true",
        help="在agent模式下启用MCP工具加载（来自MCP_SERVERS_JSON）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "qa":
        answer = run(args.question)
    else:
        answer = asyncio.run(run_agent(args.question, enable_mcp=args.enable_mcp))
    print(answer)


if __name__ == "__main__":
    main()
