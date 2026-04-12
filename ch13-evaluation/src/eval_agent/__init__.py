"""Eval Agent — Langfuse 기반 LLM 관찰성 + 평가 유틸리티.

주요 기능:
- Langfuse 트레이싱 자동 연동
- RAG 파이프라인 추적
- 평가 점수 기록 (Faithfulness, Context Precision/Recall, Answer Relevance)
- RAGAS 기반 배치 평가
- PII 마스킹
"""

from eval_agent.config import Settings, get_settings
from eval_agent.evaluation import (
    create_score,
    evaluate_context_precision,
    evaluate_context_recall,
    evaluate_faithfulness,
    evaluate_response,
)
from eval_agent.langfuse_setup import (
    flush_langfuse,
    get_langfuse_client,
    get_langfuse_handler,
    init_langfuse,
    is_langfuse_enabled,
)
from eval_agent.rag_chain import (
    RAGAgent,
    ask_rag,
    create_rag_agent,
    retrieve_documents,
    setup_sample_vectorstore,
)

__version__ = "0.1.0"
__all__ = [
    # 설정
    "Settings",
    "get_settings",
    # Langfuse
    "init_langfuse",
    "is_langfuse_enabled",
    "get_langfuse_client",
    "get_langfuse_handler",
    "flush_langfuse",
    # RAG
    "ask_rag",
    "RAGAgent",
    "create_rag_agent",
    "retrieve_documents",
    "setup_sample_vectorstore",
    # 평가
    "evaluate_response",
    "evaluate_faithfulness",
    "evaluate_context_precision",
    "evaluate_context_recall",
    "create_score",
    # 배치 평가 (RAGAS)
    "evaluate_rag_batch",
]


def __getattr__(name: str):  # pragma: no cover - lazy import
    """RAGAS는 무거운 의존성이므로 필요할 때만 로드한다."""
    if name == "evaluate_rag_batch":
        from eval_agent.ragas_eval import evaluate_rag_batch

        return evaluate_rag_batch
    raise AttributeError(f"module 'eval_agent' has no attribute {name!r}")
