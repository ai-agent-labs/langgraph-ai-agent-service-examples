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

    langfuse_public_key: SecretStr | None = Field(
        default=None, description="Langfuse Public Key"
    )
    langfuse_secret_key: SecretStr | None = Field(
        default=None, description="Langfuse Secret Key"
    )
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com", description="Langfuse 호스트"
    )
    langfuse_sample_rate: float = Field(
        default=1.0, description="Langfuse 샘플링 비율 (0.0~1.0)"
    )
    langfuse_enable_masking: bool = Field(
        default=False, description="PII 마스킹 활성화"
    )

    default_model: str = Field(default="gpt-5.2", description="기본 LLM 모델")
    embedding_model: str = Field(
        default="text-embedding-3-small", description="임베딩 모델"
    )

    search_top_k: int = Field(default=3, description="검색 결과 수")
    debug: bool = Field(default=False, description="디버그 모드")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
