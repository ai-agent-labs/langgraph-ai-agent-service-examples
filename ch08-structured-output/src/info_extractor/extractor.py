from langchain.chat_models import init_chat_model
from pydantic import BaseModel

from info_extractor.config import get_settings
from info_extractor.schemas import ContactInfo, LeaveRequest, MovieInfo


def create_structured_model(schema: type[BaseModel], model_name: str | None = None):
    """주어진 스키마로 구조화 출력을 생성하는 모델을 만듭니다."""
    settings = get_settings()
    model_name = model_name or settings.default_model

    model = init_chat_model(
        model_name,
        model_provider="openai",
        temperature=settings.temperature,
    )
    return model.with_structured_output(schema)


def extract_leave_request(text: str) -> LeaveRequest:
    """자유 형식 텍스트에서 휴가 신청 정보를 추출합니다."""
    structured_llm = create_structured_model(LeaveRequest)
    return structured_llm.invoke(
        f"다음 요청에서 휴가 신청 정보를 추출하세요: {text}"
    )


def extract_contact_info(text: str) -> ContactInfo:
    """자유 형식 텍스트에서 연락처 정보를 추출합니다."""
    structured_llm = create_structured_model(ContactInfo)
    return structured_llm.invoke(f"다음 텍스트에서 연락처 정보를 추출하세요: {text}")


def extract_movie_info(text: str) -> MovieInfo:
    """자유 형식 텍스트에서 영화 정보를 추출합니다."""
    structured_llm = create_structured_model(MovieInfo)
    return structured_llm.invoke(f"다음 텍스트에서 영화 정보를 추출하세요: {text}")
