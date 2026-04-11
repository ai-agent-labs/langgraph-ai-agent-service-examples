from typing import TypedDict


class HRRequestState(TypedDict):
    query: str  # 직원 요청
    category: str  # 분류 결과
    response: str  # 최종 응답
