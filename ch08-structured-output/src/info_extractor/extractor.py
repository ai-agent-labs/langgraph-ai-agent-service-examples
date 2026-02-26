from langchain.chat_models import init_chat_model
from pydantic import BaseModel

from info_extractor.config import get_settings
from info_extractor.schemas import ContactInfo, MovieInfo


def create_structured_model(schema: type[BaseModel], model_name: str | None = None):
    settings = get_settings()
    model_name = model_name or settings.default_model

    model = init_chat_model(
        model_name,
        model_provider="openai",
        temperature=settings.temperature,
    )
    return model.with_structured_output(schema)


def extract_contact_info(text: str) -> ContactInfo:
    structured_llm = create_structured_model(ContactInfo)
    return structured_llm.invoke(f"다음 텍스트에서 연락처 정보를 추출하세요: {text}")


def extract_movie_info(text: str) -> MovieInfo:
    structured_llm = create_structured_model(MovieInfo)
    return structured_llm.invoke(f"다음 텍스트에서 영화 정보를 추출하세요: {text}")
