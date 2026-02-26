from datetime import datetime

from langchain_core.tools import tool


EMPLOYEES = {
    "EMP001": {"name": "김철수", "total_leave": 15, "used_leave": 3},
    "EMP002": {"name": "이영희", "total_leave": 15, "used_leave": 7},
}

BENEFITS = {
    "건강검진": {"limit": 50, "period": "상반기(3-6월)", "note": "복지 포털에서 예약"},
    "교육비": {"limit": 100, "period": "연중", "note": "100만원 초과 시 HR 승인 필요"},
    "통신비": {"limit": 5, "period": "월별", "note": "매월 자동 지급"},
    "식대": {"limit": 10, "period": "월별", "note": "복지카드로 사용"},
}

POLICIES = {
    "연차": "입사 1년차 직원은 15일의 연차가 부여됩니다.",
    "재택": "재택근무는 주 2회까지 가능하며, 전날 17시까지 신청해야 합니다.",
    "야근": "야근 시 식대와 택시비가 지원됩니다.",
}


@tool
def get_leave_balance(employee_id: str) -> dict:
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


@tool
def request_leave(employee_id: str, start_date: str, days: int) -> dict:
    """휴가를 신청합니다."""
    employee = EMPLOYEES.get(employee_id)
    if not employee:
        return {"error": f"직원 ID '{employee_id}'를 찾을 수 없습니다."}

    remaining = employee["total_leave"] - employee["used_leave"]
    if days > remaining:
        return {"error": f"잔여 연차({remaining}일)가 부족합니다."}

    return {
        "status": "approved",
        "request_id": f"LEAVE-{datetime.now().strftime('%H%M%S')}",
        "message": f"{employee['name']}님의 {start_date}부터 {days}일 휴가가 승인되었습니다.",
    }


@tool
def get_benefit_info(benefit_type: str) -> dict:
    """복리후생 정보를 조회합니다."""
    benefit = BENEFITS.get(benefit_type)
    if not benefit:
        available = ", ".join(BENEFITS.keys())
        return {"error": f"'{benefit_type}'은 찾을 수 없습니다. 사용 가능: {available}"}

    return {
        "benefit": benefit_type,
        "limit": f"{benefit['limit']}만원",
        "period": benefit["period"],
        "note": benefit["note"],
    }


@tool
def apply_benefit(employee_id: str, benefit_type: str, amount: int) -> dict:
    """복리후생을 신청합니다."""
    benefit = BENEFITS.get(benefit_type)
    if not benefit:
        return {"error": f"'{benefit_type}'은 지원되지 않습니다."}

    if amount > benefit["limit"] * 10000:
        return {"error": f"한도({benefit['limit']}만원)를 초과했습니다."}

    return {
        "status": "approved",
        "request_id": f"BEN-{datetime.now().strftime('%H%M%S')}",
        "message": f"{benefit_type} {amount:,}원 신청이 완료되었습니다.",
    }


@tool
def search_policy(keyword: str) -> dict:
    """정책을 검색합니다."""
    results = []
    for key, value in POLICIES.items():
        if keyword.lower() in key.lower() or keyword.lower() in value.lower():
            results.append({"topic": key, "content": value})

    if not results:
        return {"message": f"'{keyword}' 관련 정책을 찾을 수 없습니다."}

    return {"results": results}


LEAVE_TOOLS = [get_leave_balance, request_leave]
BENEFIT_TOOLS = [get_benefit_info, apply_benefit]
POLICY_TOOLS = [search_policy]
