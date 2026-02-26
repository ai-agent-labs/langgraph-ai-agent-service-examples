from functools import lru_cache

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

    opensearch_host: str = Field(default="localhost", description="OpenSearch 호스트")
    opensearch_port: int = Field(default=9200, description="OpenSearch 포트")
    opensearch_user: str | None = Field(default=None, description="OpenSearch 사용자")
    opensearch_password: SecretStr | None = Field(
        default=None, description="OpenSearch 비밀번호"
    )

    default_model: str = Field(default="gpt-5.2", description="기본 LLM 모델")
    embedding_model: str = Field(
        default="text-embedding-3-small", description="임베딩 모델"
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2", description="리랭킹 모델"
    )

    index_name: str = Field(default="company-docs", description="인덱스 이름")
    chunk_size: int = Field(default=500, description="청크 크기")
    chunk_overlap: int = Field(default=50, description="청크 오버랩")
    search_top_k: int = Field(default=5, description="검색 결과 수")
    rerank_top_k: int = Field(default=3, description="리랭킹 후 결과 수")

    vector_weight: float = Field(default=0.7, description="벡터 검색 가중치")
    keyword_weight: float = Field(default=0.3, description="키워드 검색 가중치")

    debug: bool = Field(default=False, description="디버그 모드")

    @property
    def opensearch_url(self) -> str:
        return f"http://{self.opensearch_host}:{self.opensearch_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
