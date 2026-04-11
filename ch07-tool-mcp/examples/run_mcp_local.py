"""
7.2-4절 실습: 로컬 MCP 서버의 도구를 LangChain 에이전트에 바인딩.

로컬 stdio MCP 서버(``mcp_server_example/hr_server.py``)를 서브프로세스로
띄운 뒤 ``load_mcp_tools`` 로 도구 목록을 LangChain 형식으로 받아와
``create_agent`` 로 에이전트를 구성해 질의합니다.

실행:
    cd ch07-tool-mcp
    uv sync                           # langchain-mcp-adapters / mcp 설치
    uv run python examples/run_mcp_local.py

``.env`` 에 ``OPENAI_API_KEY`` 가 설정되어 있어야 합니다.
"""

from __future__ import annotations

import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from hr_assistant.mcp_integration import fetch_local_mcp_tools

load_dotenv()


async def main() -> None:
    print("[MCP] 로컬 서버에서 도구 목록 로드 중...")
    tools = await fetch_local_mcp_tools()
    print(f"[MCP] 도구 {len(tools)}개 로드: {[t.name for t in tools]}")

    model = init_chat_model(model_provider="openai", model="gpt-5.2")
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "당신은 HR 어시스턴트입니다. 사용자의 요청에 맞는 MCP 도구를 "
            "호출해 정확한 답변을 제공하세요."
        ),
    )

    for query in [
        "EMP001의 연차 잔여일수 알려줘",
        "재택근무 정책 알려줘",
    ]:
        print(f"\n== 질문: {query}")
        result = await agent.ainvoke({"messages": [("user", query)]})
        final = result["messages"][-1]
        print(f"답변: {final.content}")


if __name__ == "__main__":
    asyncio.run(main())
