# RAG Agent - 5장 실습 프로젝트

> AI 에이전트 개발 기술서 5장 "RAG" 실습 프로젝트입니다.

이 프로젝트는 OpenSearch를 사용한 RAG(Retrieval-Augmented Generation) 시스템을 구현합니다.

## 목차

- [요구사항](#요구사항)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [실습 내용](#실습-내용)
- [사용 방법](#사용-방법)
- [문제 해결](#문제-해결)

## 요구사항

- **Python**: 3.12 이상
- **Docker**: OpenSearch 실행용
- **패키지 관리자**: [uv](https://docs.astral.sh/uv/) (권장) 또는 pip
- **API 키**: OpenAI

## 빠른 시작

### 1. uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 프로젝트 설정

```bash
# 디렉토리 이동
cd ch05-rag

# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
# .env 파일을 열고 OPENAI_API_KEY 입력
```

### 3. OpenSearch 시작

```bash
# OpenSearch 시작
docker compose up -d

# 연결 확인 (몇 초 대기 후)
curl http://localhost:9200
```

### 4. 샘플 데이터 인덱싱 및 앱 실행

```bash
# 웹 UI 실행
uv run streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속 후, 사이드바에서 "샘플 데이터 인덱싱"을 클릭합니다.

## 프로젝트 구조

```
ch05-rag/
├── src/
│   └── rag_agent/
│       ├── __init__.py       # 패키지 초기화
│       ├── config.py         # 설정 관리
│       ├── document.py       # 문서 청킹
│       ├── embeddings.py     # 임베딩 처리
│       ├── indexer.py        # OpenSearch 인덱싱
│       ├── search.py         # 벡터/하이브리드 검색
│       ├── reranker.py       # Cross-Encoder 리랭킹
│       ├── rag_chain.py      # RAG 체인
│       └── agentic_rag.py    # 에이전틱 RAG (LangGraph)
├── data/
│   └── sample_docs/          # 샘플 문서 (선택)
├── docker-compose.yml        # OpenSearch 설정
├── .env.example              # 환경변수 템플릿
├── .gitignore                # Git 제외 파일
├── .python-version           # Python 버전
├── pyproject.toml            # 프로젝트 설정
├── app.py                    # Streamlit 웹 앱
└── README.md                 # 이 파일
```

## 실습 내용

### 7.3 RAG 구현

```python
from rag_agent import setup_sample_index, ask_rag

# 샘플 문서 인덱싱
setup_sample_index()

# RAG로 질문
answer = ask_rag("연차휴가는 며칠인가요?")
print(answer)
```

### 7.4 하이브리드 검색

```python
from rag_agent import hybrid_search

# 하이브리드 검색 (벡터 + 키워드)
results = hybrid_search(
    query="재택근무 신청",
    k=5,
    vector_weight=0.7,
    keyword_weight=0.3,
)

for r in results:
    print(f"[{r['score']:.3f}] {r['content'][:50]}...")
```

### 7.5 Cross-Encoder 리랭킹

```python
from rag_agent import search_with_rerank

# 하이브리드 검색 + 리랭킹
results = search_with_rerank(
    query="출장 정산 방법",
    initial_k=10,
    final_k=3,
)

for r in results:
    print(f"[{r['rerank_score']:.3f}] {r['content'][:50]}...")
```

### 7.6 에이전틱 RAG

```python
from rag_agent import ask_agentic_rag

# 복잡한 질문 - 에이전트가 필요에 따라 여러 번 검색
answer = ask_agentic_rag(
    "연차휴가 신청 방법과 재택근무 신청 방법을 비교해서 알려주세요"
)
print(answer)
```

## 사용 방법

### 웹 UI (Streamlit)

```bash
uv run streamlit run app.py
```

**기능:**

- 기본 RAG / 에이전틱 RAG 모드 선택
- 벡터/하이브리드 검색 방식 선택
- 리랭킹 on/off
- 실시간 스트리밍 응답

### Python 코드에서 사용

```python
from rag_agent import create_rag_agent

# RAG 에이전트 생성
agent = create_rag_agent(
    search_type="hybrid",
    use_rerank=True,
)

# 대화
response = agent.chat("연차휴가 신청 방법을 알려주세요")
print(response)

# 스트리밍 응답
for chunk in agent.stream("재택근무는 몇 일까지 가능한가요?"):
    print(chunk, end="", flush=True)
```

## 설정

### 환경변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `OPENSEARCH_HOST` | OpenSearch 호스트 | `localhost` |
| `OPENSEARCH_PORT` | OpenSearch 포트 | `9200` |
| `DEFAULT_MODEL` | 기본 LLM 모델 | `gpt-5.2` |
| `EMBEDDING_MODEL` | 임베딩 모델 | `text-embedding-3-small` |
| `CHUNK_SIZE` | 청크 크기 | `500` |
| `VECTOR_WEIGHT` | 벡터 검색 가중치 | `0.7` |

### OpenSearch 관리

```bash
# 시작
docker compose up -d

# 중지
docker compose down

# 데이터 포함 삭제
docker compose down -v

# 대시보드 포함 시작 (선택)
docker compose --profile dashboards up -d
# http://localhost:5601 에서 확인
```

## 문제 해결

### OpenSearch 연결 실패

```
ConnectionError: Connection refused
```

**해결:**
```bash
# OpenSearch 상태 확인
docker compose ps

# 로그 확인
docker compose logs opensearch

# 재시작
docker compose restart
```

### 인덱스 없음 오류

```
NotFoundError: index_not_found_exception
```

**해결:** 앱에서 "샘플 데이터 인덱싱" 버튼 클릭 또는:
```python
from rag_agent import setup_sample_index
setup_sample_index()
```

### 리랭킹 모델 다운로드 느림

처음 실행 시 Cross-Encoder 모델(~90MB)을 다운로드합니다. 잠시 기다려주세요.

### 메모리 부족

OpenSearch가 메모리를 많이 사용합니다. `docker-compose.yml`에서 메모리 설정을 조정하세요:
```yaml
environment:
  - "OPENSEARCH_JAVA_OPTS=-Xms256m -Xmx256m"  # 기본 512m
```

## 참고 자료

- [LangChain RAG 튜토리얼](https://python.langchain.com/docs/tutorials/rag/)
- [OpenSearch k-NN 문서](https://opensearch.org/docs/latest/search-plugins/knn/)
- [Sentence Transformers](https://www.sbert.net/)

## 라이선스

MIT License

---

**AI 에이전트 개발 기술서** - 5장 "RAG" 실습 프로젝트
