"""
7.2절 실습용 간이 MCP 서버.

``ch07-tool-mcp/src/hr_assistant/tools.py`` 의 HR 도구(연차 조회, 정책 검색,
휴가 신청)를 MCP 프로토콜을 통해 외부에 노출한다. 독자는 별도 클라우드
서버 없이도 이 스크립트를 실행해 MCP 클라이언트-서버 구조를 실습할 수 있다.

실행:
    python mcp_server_example/hr_server.py

또는 MCP 클라이언트가 stdio 로 자동 기동(``StdioServerParameters``) 한다.
"""

from __future__ import annotations

from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hr-assistant")


EMPLOYEES = {
    "EMP001": {"name": "김철수", "total_leave": 15, "used_leave": 3},
    "EMP002": {"name": "이영희", "total_leave": 15, "used_leave": 7},
}

POLICIES = {
    "재택": "재택근무는 주 2회까지 가능하며, 전날 17시까지 신청해야 합니다.",
    "경조사": "경조사 휴가는 본인 결혼 5일, 자녀 결혼 1일, 부모 사망 5일이 부여됩니다.",
    "교육비": "교육비는 연간 100만원까지 지원됩니다.",
}


@mcp.tool()
def check_leave_balance(employee_id: str) -> dict:
    """직원의 연차 잔여일수를 조회합니다."""
    employee = EMPLOYEES.get(employee_id)
    if not employee:
        return {"error": f"직원 ID '{employee_id}'를 찾을 수 없습니다."}
    return {
        "employee_id": employee_id,
        "name": employee["name"],
        "remaining": employee["total_leave"] - employee["used_leave"],
        "total": employee["total_leave"],
    }


@mcp.tool()
def search_policy(keyword: str) -> dict:
    """키워드로 HR 정책을 검색합니다."""
    results = [
        {"topic": key, "content": value}
        for key, value in POLICIES.items()
        if keyword in key or keyword in value
    ]
    if not results:
        return {"message": f"'{keyword}' 관련 정책을 찾을 수 없습니다."}
    return {"results": results}


@mcp.tool()
def submit_leave_request(
    employee_id: str,
    start_date: str,
    end_date: str,
    reason: str,
) -> dict:
    """휴가 신청서를 제출합니다."""
    employee = EMPLOYEES.get(employee_id)
    if not employee:
        return {"error": f"직원 ID '{employee_id}'를 찾을 수 없습니다."}
    return {
        "status": "approved",
        "request_id": f"LEAVE-{datetime.now().strftime('%H%M%S')}",
        "employee_id": employee_id,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
    }


if __name__ == "__main__":
    mcp.run()
