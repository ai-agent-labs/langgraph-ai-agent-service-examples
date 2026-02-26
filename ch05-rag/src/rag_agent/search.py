from opensearchpy import OpenSearch

from rag_agent.config import get_settings
from rag_agent.embeddings import create_embeddings
from rag_agent.indexer import create_opensearch_client


def vector_search(
    query: str,
    k: int | None = None,
    client: OpenSearch | None = None,
    index_name: str | None = None,
) -> list[dict]:
    settings = get_settings()
    client = client or create_opensearch_client()
    index_name = index_name or settings.index_name
    k = k or settings.search_top_k

    # 질문을 벡터로 변환
    embeddings = create_embeddings()
    query_vector = embeddings.embed_query(query)

    # k-NN 검색 쿼리
    search_query = {
        "size": k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_vector,
                    "k": k,
                }
            }
        },
    }

    # 검색 실행
    response = client.search(index=index_name, body=search_query)

    # 결과 추출
    results = []
    for hit in response["hits"]["hits"]:
        results.append(
            {
                "content": hit["_source"]["content"],
                "score": hit["_score"],
                "metadata": hit["_source"].get("metadata", {}),
                "id": hit["_id"],
            }
        )

    return results


def keyword_search(
    query: str,
    k: int | None = None,
    client: OpenSearch | None = None,
    index_name: str | None = None,
) -> list[dict]:
    settings = get_settings()
    client = client or create_opensearch_client()
    index_name = index_name or settings.index_name
    k = k or settings.search_top_k

    # BM25 검색 쿼리
    search_query = {
        "size": k,
        "query": {
            "match": {
                "content": query,
            }
        },
    }

    # 검색 실행
    response = client.search(index=index_name, body=search_query)

    # 결과 추출
    results = []
    for hit in response["hits"]["hits"]:
        results.append(
            {
                "content": hit["_source"]["content"],
                "score": hit["_score"],
                "metadata": hit["_source"].get("metadata", {}),
                "id": hit["_id"],
            }
        )

    return results


def hybrid_search(
    query: str,
    k: int | None = None,
    vector_weight: float | None = None,
    keyword_weight: float | None = None,
    client: OpenSearch | None = None,
    index_name: str | None = None,
) -> list[dict]:
    settings = get_settings()
    k = k or settings.search_top_k
    vector_weight = vector_weight if vector_weight is not None else settings.vector_weight
    keyword_weight = (
        keyword_weight if keyword_weight is not None else settings.keyword_weight
    )

    # 각 검색 방식으로 더 많은 후보 추출
    candidate_k = k * 3

    # 벡터 검색
    vector_results = vector_search(
        query, k=candidate_k, client=client, index_name=index_name
    )

    # 키워드 검색
    keyword_results = keyword_search(
        query, k=candidate_k, client=client, index_name=index_name
    )

    # RRF로 점수 병합
    rrf_k = 60  # RRF 파라미터
    rrf_scores: dict[str, dict] = {}

    # 벡터 검색 결과에 RRF 점수 부여
    for rank, result in enumerate(vector_results):
        doc_id = result["id"]
        rrf_score = vector_weight / (rrf_k + rank + 1)

        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = {
                "content": result["content"],
                "metadata": result["metadata"],
                "score": 0,
                "vector_rank": rank + 1,
                "keyword_rank": None,
            }
        rrf_scores[doc_id]["score"] += rrf_score
        rrf_scores[doc_id]["vector_rank"] = rank + 1

    # 키워드 검색 결과에 RRF 점수 추가
    for rank, result in enumerate(keyword_results):
        doc_id = result["id"]
        rrf_score = keyword_weight / (rrf_k + rank + 1)

        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = {
                "content": result["content"],
                "metadata": result["metadata"],
                "score": 0,
                "vector_rank": None,
                "keyword_rank": rank + 1,
            }
        rrf_scores[doc_id]["score"] += rrf_score
        rrf_scores[doc_id]["keyword_rank"] = rank + 1

    # 점수순 정렬
    sorted_results = sorted(
        [{"id": doc_id, **data} for doc_id, data in rrf_scores.items()],
        key=lambda x: x["score"],
        reverse=True,
    )

    return sorted_results[:k]


def format_search_results(results: list[dict], include_score: bool = True) -> str:
    formatted_parts = []

    for i, result in enumerate(results, 1):
        source = result.get("metadata", {}).get("source", "unknown")
        chunk_idx = result.get("metadata", {}).get("chunk_index", "?")

        if include_score:
            header = f"[문서 {i}] 출처: {source}, 청크 {chunk_idx}, 점수: {result['score']:.3f}"
        else:
            header = f"[문서 {i}] 출처: {source}, 청크 {chunk_idx}"

        formatted_parts.append(f"{header}\n{result['content']}")

    return "\n\n---\n\n".join(formatted_parts)
