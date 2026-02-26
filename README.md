# LangGraph로 만드는 AI 에이전트 서비스 - 실습 예제

이 저장소는 도서 **LangGraph로 만드는 AI 에이전트 서비스**의 독자용 실습 예제를 모아둔 독립 공개 저장소입니다.
LangChain/LangGraph 기반 예제를 챕터별로 실행하면서 핵심 개념을 직접 확인할 수 있습니다.

## 도서 안내

- 도서명: LangGraph로 만드는 AI 에이전트 서비스 — LangChain 기초부터 RAG, 멀티 에이전트, 평가까지 한 권으로 끝내기
- 저자: 전상우, 정영훈, 서평원, 이정훈, 이민혁
- 출판사: (주)도서출판 성안당

## 빠른 시작

### 저장소 클론 및 통합 앱 실행

```bash
git clone https://github.com/ai-agent-labs/langgraph-ai-agent-service-examples.git && cd langgraph-ai-agent-service-examples
cp .env.example .env
uv sync
uv run streamlit run app.py
```

### 개별 챕터 실행

```bash
cd ch03-langchain-basics
uv sync
uv run streamlit run app.py
```

## 챕터 구성

| 디렉토리 | 챕터 | 주제 |
|---|---|---|
| `ch02-getting-started` | Ch02 | 개발 시작하기 |
| `ch03-langchain-basics` | Ch03 | LangChain 기본 체인 |
| `ch05-rag` | Ch05 | RAG 검색 |
| `ch06-memory` | Ch06 | 대화 메모리 |
| `ch07-tool-mcp` | Ch07 | 도구 호출과 MCP |
| `ch08-structured-output` | Ch08 | 구조화된 출력 |
| `ch09-langgraph` | Ch09 | LangGraph 라우팅 |
| `ch10-single-agent` | Ch10 | 단일 에이전트 |
| `ch11-multi-agent` | Ch11 | 멀티 에이전트 |
| `ch13-evaluation` | Ch13 | 평가와 모니터링 |

## 권장 학습 순서

```text
Ch02 (시작) → Ch03 (기초 체인) → Ch06 (메모리) → Ch07 (도구/MCP) → Ch08 (구조화)
                                                      ↓
                                              Ch09 (LangGraph)
                                                      ↓
                                              Ch10 (단일 에이전트)
                                                      ↓
                                              Ch11 (멀티 에이전트)
                                                      ↓
                                         Ch05 (RAG) → Ch13 (평가)
```

## 기술 스택

- Python 3.11 이상
- LangChain >=0.3.25
- LangChain Core >=0.3.61
- LangGraph >=0.4.8
- LangGraph Supervisor >=0.0.12
- Streamlit >=1.45.1

## 디렉토리 구조

```text
.
├── .env.example
├── app.py
├── pyproject.toml
├── uv.lock
├── shared/
│   ├── navigation.py
│   ├── styles.py
│   └── utils.py
├── ch02-getting-started/
├── ch03-langchain-basics/
├── ch05-rag/
├── ch06-memory/
├── ch07-tool-mcp/
├── ch08-structured-output/
├── ch09-langgraph/
├── ch10-single-agent/
├── ch11-multi-agent/
└── ch13-evaluation/
```

## 환경 설정

`.env` 파일을 만들고 값을 입력하세요.

```bash
# 필수
OPENAI_API_KEY=sk-proj-...

# Ch05 RAG (선택)
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200

# Ch13 평가 (선택)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
```

## 예제 도메인

예제는 HR(인사) 시나리오를 중심으로 구성되어 있습니다.

- 연차/휴가 질의응답
- 복리후생 안내
- 사내 정책 검색
- 온보딩 지원
