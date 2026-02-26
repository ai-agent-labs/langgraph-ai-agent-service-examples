from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openai_api_key: SecretStr = Field(..., description="OpenAI API 키")
    default_model: str = Field(default="gpt-5.2", description="기본 모델 이름")
    debug: bool = Field(default=False, description="디버그 모드")


def get_settings() -> Settings:
    return Settings()
