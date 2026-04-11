from pydantic import BaseModel, Field


class LeaveRequest(BaseModel):
    """휴가 신청 정보를 추출한 결과입니다."""

    employee_id: str = Field(
        description="직원 ID. 예: EMP001, EMP002"
    )
    leave_type: str = Field(
        description="휴가 유형. 연차, 반차, 병가, 경조사 중 하나를 선택합니다."
    )
    start_date: str = Field(
        description="휴가 시작일. YYYY-MM-DD 형식으로 작성합니다."
    )
    end_date: str = Field(
        description="휴가 종료일. YYYY-MM-DD 형식으로 작성합니다."
    )
    reason: str = Field(
        description="휴가 사유를 간단히 요약합니다."
    )
