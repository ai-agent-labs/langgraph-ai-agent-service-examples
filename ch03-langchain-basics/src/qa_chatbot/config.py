from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: SecretStr = Field(..., description="OpenAI API 키")
    default_model: str = Field(default="gpt-5.2", description="기본 LLM 모델")
    temperature: float = Field(default=0.7, description="생성 온도 (0.0~1.0)")
    max_tokens: int = Field(default=1000, description="최대 토큰 수")


@lru_cache
def get_settings() -> Settings:
    return Settings()
