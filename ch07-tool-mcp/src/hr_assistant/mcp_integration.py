"""MCP와 LangChain 통합.

외부 HTTP MCP 서버와 로컬 stdio MCP 서버에 각각 연결하는 두 경로를 제공한다.
독자가 Smithery 계정 없이도 실습할 수 있도록 로컬 stdio 방식이 fallback.

1. **원격 HTTP MCP 서버** (``fetch_remote_mcp_tools``)
   - ``streamablehttp_client`` 로 원격 MCP 서버에 연결.
   - 환경 변수 ``MCP_SERVER_URL``에 Smithery 등에서 얻은 URL을 설정해야 동작.

2. **로컬 stdio MCP 서버** (``fetch_local_mcp_tools``)
   - ``mcp_server_example/hr_server.py`` 에 포함된 간이 MCP 서버를
     ``uv run python mcp_server_example/hr_server.py`` 로 서브프로세스 실행.
   - 외부 네트워크 / 인증 키 없이도 실습 가능.

두 함수 모두 반환 값은 ``list[BaseTool]`` 로, LangChain 에이전트에
그대로 ``bind_tools`` 또는 ``create_agent`` 에 전달할 수 있다.
"""

from __future__ import annotations

import os
from pathlib import Path


async def fetch_remote_mcp_tools() -> list:
    """Smithery 등 외부 HTTP MCP 서버에 연결해 도구 목록을 로드.

    환경 변수 ``MCP_SERVER_URL`` 에 MCP 서버 URL이 설정되어 있어야 한다.
    """
    from langchain_mcp_adapters.tools import load_mcp_tools
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    url = os.getenv("MCP_SERVER_URL")
    if not url:
        raise RuntimeError(
            "MCP_SERVER_URL 환경 변수가 설정되지 않았습니다. "
            "Smithery 등에서 받은 MCP 서버 URL을 .env에 추가하세요."
        )

    async with streamablehttp_client(url) as (read, write, _close):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            return await load_mcp_tools(mcp_session)


async def fetch_local_mcp_tools() -> list:
    """로컬 stdio MCP 서버에 연결해 도구 목록을 로드.

    Smithery 계정이나 인터넷 접근이 없어도 실습할 수 있도록 ``mcp_server_example/hr_server.py``
    를 서브프로세스로 띄워 연결한다.
    """
    from langchain_mcp_adapters.tools import load_mcp_tools
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_script = (
        Path(__file__).resolve().parents[2]
        / "mcp_server_example"
        / "hr_server.py"
    )
    if not server_script.exists():
        raise FileNotFoundError(
            f"로컬 MCP 서버 스크립트를 찾을 수 없습니다: {server_script}"
        )

    params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            return await load_mcp_tools(mcp_session)
