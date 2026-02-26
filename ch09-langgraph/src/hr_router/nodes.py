from hr_router.state import HRRequestState


def classify_node(state: HRRequestState) -> dict:
    """요청 유형 분류"""
    query = state["query"].lower()

    if "경조사" in query or "휴가" in query or "근태" in query:
        category = "leave"
    elif "건강검진" in query or "교육비" in query or "복지" in query:
        category = "benefit"
    elif "재택" in query or "규정" in query or "정책" in query:
        category = "policy"
    elif "온보딩" in query or "계정" in query or "장비" in query:
        category = "onboarding"
    else:
        category = "general"

    return {"category": category}


def route_query(state: HRRequestState) -> str:
    """분류 결과에 따라 다음 노드 결정"""
    return state["category"]


def leave_node(state: HRRequestState) -> dict:
    """휴가/근태 응답"""
    return {"response": "경조사 휴가는 본인 결혼 5일, 자녀 결혼 1일, 부모 사망 5일이 부여됩니다. HR 포털에서 증빙 서류와 함께 신청하세요."}


def benefit_node(state: HRRequestState) -> dict:
    """복리후생 응답"""
    return {"response": "건강검진은 매년 상반기에 신청 가능하며, 복지 포털에서 예약하실 수 있습니다."}


def policy_node(state: HRRequestState) -> dict:
    """정책/규정 응답"""
    return {"response": "재택근무는 주 2회까지 가능하며, 전날 17시까지 신청해야 합니다."}


def onboarding_node(state: HRRequestState) -> dict:
    """온보딩/오프보딩 응답"""
    return {"response": "IT 계정은 입사일에 자동 발급되며, 장비는 총무팀에서 수령 가능합니다."}


def general_node(state: HRRequestState) -> dict:
    """일반 요청 응답"""
    return {"response": "HR 센터로 문의해주세요. 담당자가 확인 후 연락드리겠습니다."}
