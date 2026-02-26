from datetime import datetime
from typing import Literal

from langchain_core.tools import tool

from hr_assistant.data import get_employee_data, search_policies, add_leave_request


@tool
def check_leave_balance(employee_id: str) -> dict:
    """직원의 연차 잔여일수를 조회합니다.

    Args:
        employee_id: 직원 ID (예: EMP001)
    """
    employee = get_employee_data(employee_id)
    if not employee:
        return {"status": "error", "message": f"직원 ID '{employee_id}'를 찾을 수 없습니다."}

    return {
        "status": "success",
        "data": {
            "employee_id": employee_id,
            "name": employee["name"],
            "total_days": employee["total_leave"],
            "used_days": employee["used_leave"],
            "remaining_days": employee["total_leave"] - employee["used_leave"],
        },
    }


@tool
def search_policy(
    keyword: str,
    category: Literal["leave", "remote_work", "benefit", "all"] = "all",
) -> dict:
    """HR 정책을 키워드로 검색합니다.

    Args:
        keyword: 검색할 키워드 (예: 연차, 재택, 교육비)
        category: 정책 카테고리 (leave, remote_work, benefit, all)
    """
    results = search_policies(keyword, category)
    if not results:
        return {"status": "success", "data": {"matches": [], "message": "검색 결과가 없습니다."}}

    return {"status": "success", "data": {"matches": results, "count": len(results)}}


@tool
def submit_leave_request(
    employee_id: str,
    start_date: str,
    end_date: str,
    reason: str,
) -> dict:
    """휴가 신청을 제출합니다.

    Args:
        employee_id: 직원 ID (예: EMP001)
        start_date: 휴가 시작일 (YYYY-MM-DD)
        end_date: 휴가 종료일 (YYYY-MM-DD)
        reason: 휴가 사유
    """
    employee = get_employee_data(employee_id)
    if not employee:
        return {"status": "error", "message": f"직원 ID '{employee_id}'를 찾을 수 없습니다."}

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {"status": "error", "message": "날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요."}

    if start > end:
        return {"status": "error", "message": "시작일이 종료일보다 늦을 수 없습니다."}

    if not reason or len(reason) < 2:
        return {"status": "error", "message": "휴가 사유를 입력해주세요."}

    days = (end - start).days + 1
    remaining = employee["total_leave"] - employee["used_leave"]
    if days > remaining:
        return {"status": "error", "message": f"잔여 연차({remaining}일)가 부족합니다. 신청일수: {days}일"}

    request_id = add_leave_request({
        "employee_id": employee_id,
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
        "reason": reason,
    })

    return {
        "status": "success",
        "data": {
            "request_id": request_id,
            "message": f"휴가 신청이 완료되었습니다. (신청번호: {request_id})",
            "details": {
                "employee": employee["name"],
                "period": f"{start_date} ~ {end_date}",
                "days": days,
            },
        },
    }


HR_TOOLS = [check_leave_balance, search_policy, submit_leave_request]
