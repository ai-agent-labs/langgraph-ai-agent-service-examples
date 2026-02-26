import re

from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

from eval_agent.config import get_settings

_initialized: bool = False
_langfuse: Langfuse | None = None
_handler: CallbackHandler | None = None
_enabled: bool = False


def is_langfuse_enabled() -> bool:
    settings = get_settings()
    return (
        settings.langfuse_public_key is not None
        and settings.langfuse_secret_key is not None
    )


def pii_masker(data, **kwargs) -> str:
    if not isinstance(data, str):
        return data

    # 이메일 마스킹
    data = re.sub(r"\b[\w.-]+@[\w.-]+\.\w+\b", "[EMAIL]", data)

    # 전화번호 마스킹 (한국 형식)
    data = re.sub(r"\b\d{2,3}-\d{3,4}-\d{4}\b", "[PHONE]", data)
    data = re.sub(r"\b01[0-9]-?\d{4}-?\d{4}\b", "[PHONE]", data)

    # 주민등록번호 마스킹
    data = re.sub(r"\b\d{6}-?\d{7}\b", "[RRN]", data)

    return data


def init_langfuse() -> Langfuse | None:
    global _initialized, _langfuse, _enabled

    if _initialized:
        return _langfuse

    settings = get_settings()

    # Langfuse 키가 없으면 비활성화
    if not is_langfuse_enabled():
        _initialized = True
        _enabled = False
        print("[INFO] Langfuse 키가 설정되지 않아 추적이 비활성화되었습니다.")
        return None

    # Langfuse 초기화 옵션
    init_kwargs = {
        "public_key": settings.langfuse_public_key.get_secret_value(),
        "secret_key": settings.langfuse_secret_key.get_secret_value(),
        "host": settings.langfuse_host,
        "sample_rate": settings.langfuse_sample_rate,
    }

    # PII 마스킹 활성화
    if settings.langfuse_enable_masking:
        init_kwargs["mask"] = pii_masker

    _langfuse = Langfuse(**init_kwargs)
    _initialized = True
    _enabled = True

    return _langfuse


def get_langfuse_client() -> Langfuse | None:
    if not _initialized:
        init_langfuse()

    if not _enabled:
        return None

    return get_client()


def get_langfuse_handler() -> CallbackHandler | None:
    global _handler

    if not _initialized:
        init_langfuse()

    if not _enabled:
        return None

    if _handler is None:
        _handler = CallbackHandler()

    return _handler


def flush_langfuse() -> None:
    if _initialized and _enabled:
        langfuse = get_client()
        langfuse.flush()
