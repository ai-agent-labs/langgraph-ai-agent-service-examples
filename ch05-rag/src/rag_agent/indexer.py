from langchain_core.documents import Document
from opensearchpy import OpenSearch

from rag_agent.config import get_settings
from rag_agent.embeddings import create_embeddings


def create_opensearch_client() -> OpenSearch:
    settings = get_settings()

    # 인증 설정
    http_auth = None
    if settings.opensearch_user and settings.opensearch_password:
        http_auth = (
            settings.opensearch_user,
            settings.opensearch_password.get_secret_value(),
        )

    return OpenSearch(
        hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
        http_auth=http_auth,
        use_ssl=False,
    )


def create_index(
    client: OpenSearch | None = None,
    index_name: str | None = None,
    vector_dimension: int = 1536,
) -> None:
    settings = get_settings()
    client = client or create_opensearch_client()
    index_name = index_name or settings.index_name

    # 인덱스 설정
    index_body = {
        "settings": {
            "index": {
                "knn": True,  # k-NN 검색 활성화
            }
        },
        "mappings": {
            "properties": {
                "content": {"type": "text"},  # 문서 내용 (키워드 검색용)
                "embedding": {
                    "type": "knn_vector",
                    "dimension": vector_dimension,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",  # 코사인 유사도
                        "engine": "nmslib",
                    },
                },
                "metadata": {"type": "object"},  # 추가 메타데이터
            }
        },
    }

    # 기존 인덱스가 있으면 삭제 후 생성
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)

    client.indices.create(index=index_name, body=index_body)

    if settings.debug:
        print(f"인덱스 '{index_name}' 생성 완료")


def index_documents(
    documents: list[Document],
    client: OpenSearch | None = None,
    index_name: str | None = None,
) -> int:
    settings = get_settings()
    client = client or create_opensearch_client()
    index_name = index_name or settings.index_name
    embeddings = create_embeddings()

    # 문서 텍스트를 벡터로 변환
    texts = [doc.page_content for doc in documents]
    vectors = embeddings.embed_documents(texts)

    # OpenSearch에 문서 저장
    for i, (doc, vector) in enumerate(zip(documents, vectors)):
        document = {
            "content": doc.page_content,
            "embedding": vector,
            "metadata": doc.metadata,
        }
        client.index(index=index_name, body=document, id=str(i))

    # 인덱스 새로고침 (검색 가능하도록)
    client.indices.refresh(index=index_name)

    if settings.debug:
        print(f"{len(documents)}개 문서 인덱싱 완료")

    return len(documents)


def setup_sample_index() -> int:
    from rag_agent.document import get_sample_chunks

    # 인덱스 생성
    create_index()

    # 샘플 문서 인덱싱
    chunks = get_sample_chunks()
    return index_documents(chunks)
