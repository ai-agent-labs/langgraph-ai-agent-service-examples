from sentence_transformers import CrossEncoder

from rag_agent.config import get_settings

# 모델 캐시 (싱글톤)
_reranker_model: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker_model

    if _reranker_model is None:
        settings = get_settings()
        _reranker_model = CrossEncoder(settings.reranker_model)

    return _reranker_model


def rerank(
    query: str,
    documents: list[dict],
    top_k: int | None = None,
) -> list[dict]:
    settings = get_settings()
    top_k = top_k or settings.rerank_top_k

    if not documents:
        return []

    # 리랭킹 모델 로드
    reranker = get_reranker()

    # 질문-문서 쌍 생성
    pairs = [[query, doc["content"]] for doc in documents]

    # 관련성 점수 계산
    scores = reranker.predict(pairs)

    # 점수 추가 및 재정렬
    for doc, score in zip(documents, scores):
        doc["rerank_score"] = float(score)

    reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_k]


def search_with_rerank(
    query: str,
    initial_k: int | None = None,
    final_k: int | None = None,
) -> list[dict]:
    from rag_agent.search import hybrid_search

    settings = get_settings()
    initial_k = initial_k or settings.search_top_k * 2
    final_k = final_k or settings.rerank_top_k

    # 1차 검색 (하이브리드)
    candidates = hybrid_search(query, k=initial_k)

    # 2차 리랭킹
    return rerank(query, candidates, top_k=final_k)
