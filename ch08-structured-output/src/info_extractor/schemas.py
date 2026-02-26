from pydantic import BaseModel, Field


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
