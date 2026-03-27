from __future__ import annotations

import argparse
import asyncio
import json

from langchain_demo import run, run_agent


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
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
        help="在agent模式下启用MCP工具加载（来自src/langchain_demo/config/mcp_servers.json）",
    )
    return parser.parse_args()


def main() -> None:
    """程序入口：执行指定模式并输出结构化结果。"""
    args = parse_args()
    if args.mode == "qa":
        response = run(args.question)
    else:
        response = asyncio.run(run_agent(args.question, enable_mcp=args.enable_mcp))
    print(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
