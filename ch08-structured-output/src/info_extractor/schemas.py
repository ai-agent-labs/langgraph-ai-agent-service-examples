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


class ContactInfo(BaseModel):
    """연락처 정보"""

    name: str = Field(description="이름")
    email: str = Field(description="이메일 주소")
    phone: str | None = Field(None, description="전화번호")


class MovieInfo(BaseModel):
    """영화 정보"""

    title: str = Field(description="영화 제목")
    year: int = Field(description="개봉 연도")
    director: str = Field(description="감독")
    rating: float = Field(description="평점 (0-10)")
