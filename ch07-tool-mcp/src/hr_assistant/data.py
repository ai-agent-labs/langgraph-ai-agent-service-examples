EMPLOYEES = {
    "EMP001": {"name": "김철수", "total_leave": 15, "used_leave": 3},
    "EMP002": {"name": "이영희", "total_leave": 15, "used_leave": 7},
    "EMP003": {"name": "박민수", "total_leave": 15, "used_leave": 12},
}

POLICIES = [
    {
        "category": "leave",
        "title": "연차휴가 사용 규정",
        "summary": "입사 1년차 직원은 15일의 연차가 부여됩니다. 연차는 당해년도 내 사용을 권장합니다.",
    },
    {
        "category": "leave",
        "title": "반차 사용 규정",
        "summary": "반차는 오전(09:00-13:00) 또는 오후(14:00-18:00)로 구분됩니다.",
    },
    {
        "category": "remote_work",
        "title": "재택근무 신청 절차",
        "summary": "재택근무는 주 2회까지 가능하며, 전날 17시까지 신청해야 합니다.",
    },
    {
        "category": "benefit",
        "title": "건강검진 지원",
        "summary": "매년 상반기(3-6월)에 건강검진을 신청할 수 있으며, 복지 포털에서 예약 가능합니다.",
    },
    {
        "category": "benefit",
        "title": "교육비 지원",
        "summary": "직무 관련 교육비는 연간 100만원까지 지원됩니다. 100만원 초과 시 HR 승인 필요.",
    },
]

LEAVE_REQUESTS: list[dict] = []


def get_employee_data(employee_id: str) -> dict | None:
    return EMPLOYEES.get(employee_id)


def search_policies(keyword: str, category: str = "all") -> list[dict]:
    results = []
    keyword_lower = keyword.lower()
    for policy in POLICIES:
        if category != "all" and policy["category"] != category:
            continue
        if keyword_lower in policy["title"].lower() or keyword_lower in policy["summary"].lower():
            results.append(policy)
    return results


def add_leave_request(request: dict) -> str:
    request_id = f"REQ-2024-{len(LEAVE_REQUESTS) + 1:03d}"
    request["request_id"] = request_id
    LEAVE_REQUESTS.append(request)
    return request_id
