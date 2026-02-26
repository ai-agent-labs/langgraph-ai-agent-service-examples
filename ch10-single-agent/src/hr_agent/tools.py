from datetime import datetime

from langchain_core.tools import tool


EMPLOYEES = {
    "EMP001": {"name": "김철수", "total_leave": 15, "used_leave": 3},
    "EMP002": {"name": "이영희", "total_leave": 15, "used_leave": 7},
    "EMP003": {"name": "박민수", "total_leave": 15, "used_leave": 12},
}

POLICIES = {
    "연차": "입사 1년차 직원은 15일의 연차가 부여됩니다.",
    "재택": "재택근무는 주 2회까지 가능하며, 전날 17시까지 신청해야 합니다.",
    "건강검진": "건강검진은 매년 상반기(3-6월)에 신청 가능합니다.",
    "교육비": "직무 관련 교육비는 연간 100만원까지 지원됩니다.",
}


@tool
def check_leave_balance(employee_id: str) -> dict:
    """직원의 연차 잔여일수를 조회합니다.

    Args:
        employee_id: 직원 ID (예: EMP001)
    """
    employee = EMPLOYEES.get(employee_id)
    if not employee:
        return {"error": f"직원 ID '{employee_id}'를 찾을 수 없습니다."}

    remaining = employee["total_leave"] - employee["used_leave"]
    return {
        "employee_id": employee_id,
        "name": employee["name"],
        "remaining_days": remaining,
        "total_days": employee["total_leave"],
        "used_days": employee["used_leave"],
    }


@tool
def submit_leave_request(
    employee_id: str,
    start_date: str,
    days: int,
    reason: str = "개인 사유",
) -> dict:
    """휴가 신청을 제출합니다.

    Args:
        employee_id: 직원 ID (예: EMP001)
        start_date: 휴가 시작일 (YYYY-MM-DD)
        days: 휴가 일수
        reason: 휴가 사유
    """
    employee = EMPLOYEES.get(employee_id)
    if not employee:
        return {"error": f"직원 ID '{employee_id}'를 찾을 수 없습니다."}

    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요."}

    remaining = employee["total_leave"] - employee["used_leave"]
    if days > remaining:
        return {"error": f"잔여 연차({remaining}일)가 부족합니다."}

    request_id = f"REQ-2024-{datetime.now().strftime('%H%M%S')}"
    return {
        "request_id": request_id,
        "status": "approved",
        "employee": employee["name"],
        "start_date": start_date,
        "days": days,
        "reason": reason,
        "message": f"휴가 신청이 완료되었습니다. (신청번호: {request_id})",
    }


@tool
def search_policy(keyword: str) -> dict:
    """HR 정책을 검색합니다.

    Args:
        keyword: 검색 키워드 (예: 연차, 재택, 건강검진)
    """
    results = []
    for key, value in POLICIES.items():
        if keyword.lower() in key.lower() or keyword.lower() in value.lower():
            results.append({"topic": key, "content": value})

    if not results:
        return {"message": f"'{keyword}' 관련 정책을 찾을 수 없습니다."}

    return {"results": results}


HR_TOOLS = [check_leave_balance, submit_leave_request, search_policy]
