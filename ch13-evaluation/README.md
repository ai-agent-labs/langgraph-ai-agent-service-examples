# RAG + Langfuse 평가 - 13장 실습 프로젝트

> AI 에이전트 개발 기술서 13장 "평가와 퀄리티" 실습 프로젝트입니다.

이 프로젝트는 Langfuse를 활용한 LLM 애플리케이션의 **관찰성(Observability)**과 **평가(Evaluation)** 시스템을 구현합니다.

## 목차

- [요구사항](#요구사항)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [실습 내용](#실습-내용)
- [사용 방법](#사용-방법)
- [Langfuse 설정](#langfuse-설정)
- [문제 해결](#문제-해결)

## 요구사항

- **Python**: 3.12 이상
- **패키지 관리자**: [uv](https://docs.astral.sh/uv/) (권장) 또는 pip
- **API 키**: OpenAI, Langfuse

## 빠른 시작

### 1. uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 프로젝트 설정

```bash
# 디렉토리 이동
cd ch13-evaluation

# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
# .env 파일을 열고 API 키 입력
```

### 3. Langfuse 설정

1. [https://cloud.langfuse.com](https://cloud.langfuse.com)에 가입합니다
2. 새 프로젝트를 생성합니다
3. Settings > API Keys에서 키를 확인합니다
4. `.env` 파일에 키를 입력합니다:

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
```

### 4. 앱 실행

```bash
uv run streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속합니다.

## 프로젝트 구조

```
ch13-evaluation/
├── src/
│   └── eval_agent/
│       ├── __init__.py       # 패키지 초기화
│       ├── config.py         # 설정 관리
│       ├── langfuse_setup.py # Langfuse 초기화
│       ├── rag_chain.py      # RAG 체인 (@observe 연동)
│       └── evaluation.py     # 평가 및 점수 기록
├── data/                     # 샘플 데이터 (선택)
├── .env.example              # 환경변수 템플릿
├── .gitignore                # Git 제외 파일
├── .python-version           # Python 버전
├── pyproject.toml            # 프로젝트 설정
├── app.py                    # Streamlit 웹 앱
└── README.md                 # 이 파일
```

## 실습 내용

### 15.2 Langfuse 연동

#### 기본 연동 - CallbackHandler

```python
from eval_agent import init_langfuse, get_langfuse_handler, flush_langfuse
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

# 1. Langfuse 초기화
init_langfuse()
handler = get_langfuse_handler()

# 2. LangChain 체인 생성
llm = init_chat_model(model_provider="openai", model="gpt-5.2", temperature=0)
prompt = ChatPromptTemplate.from_template("질문: {question}")
chain = prompt | llm

# 3. 콜백 핸들러와 함께 실행
response = chain.invoke(
    {"question": "파이썬의 장점은?"},
    config={"callbacks": [handler]}
)

# 4. 데이터 전송
flush_langfuse()
```

#### @observe 데코레이터

```python
from langfuse import observe, get_client

@observe()
def process_query(query: str) -> str:
    """함수 실행이 자동으로 Langfuse에 추적됩니다."""
    # 입력/출력, 실행 시간이 자동으로 캡처됩니다
    llm = init_chat_model(model_provider="openai", model="gpt-5.2")
    return llm.invoke(query).content

# 실행
result = process_query("안녕하세요!")

# 데이터 전송
get_client().flush()
```

#### RAG 파이프라인 추적

```python
from eval_agent import ask_rag, flush_langfuse

# RAG 파이프라인 실행 (자동 추적)
result = ask_rag("연차휴가는 며칠인가요?")
print(result["answer"])

# Langfuse 대시보드에서 확인:
# - retrieve_documents → generate_answer 호출 순서
# - 각 단계별 실행 시간
# - 검색된 문서와 생성된 답변

flush_langfuse()
```

### 15.3 평가 점수 기록

```python
from eval_agent import create_score, evaluate_response, flush_langfuse

# 자동 평가 점수 기록
result = evaluate_response(
    question="연차휴가는 며칠인가요?",
    answer="입사 1년차에 15일이 부여됩니다.",
    context="연차휴가는 입사 1년차에 15일이 부여됩니다.",
    trace_id="trace-123",  # 실제 trace_id 사용
)
print(f"Faithfulness: {result['faithfulness']:.2f}")
print(f"Relevance: {result['relevance']:.2f}")

# 사용자 피드백 기록
create_score(
    trace_id="trace-123",
    name="user-feedback",
    value=1,  # 1=좋아요, 0=싫어요
    comment="사용자가 좋아요를 눌렀습니다"
)

flush_langfuse()
```

### Best Practices

#### 샘플링으로 비용 절감

```bash
# .env 파일
LANGFUSE_SAMPLE_RATE=0.1  # 10%만 추적
```

#### PII 마스킹

```bash
# .env 파일
LANGFUSE_ENABLE_MASKING=true
```

활성화하면 다음 정보가 자동으로 마스킹됩니다:

- 이메일: `user@example.com` → `[EMAIL]`
- 전화번호: `010-1234-5678` → `[PHONE]`
- 주민등록번호: `123456-1234567` → `[RRN]`

## 사용 방법

### 웹 UI (Streamlit)

```bash
uv run streamlit run app.py
```

**기능:**

- RAG 기반 질문 답변
- 자동 Faithfulness/Relevance 평가
- 사용자 피드백 (좋아요/싫어요)
- Langfuse 트레이싱

### Python 코드에서 사용

```python
from eval_agent import create_rag_agent, flush_langfuse

# RAG 에이전트 생성
agent = create_rag_agent()

# 대화
response = agent.chat("연차휴가 신청 방법을 알려주세요")
print(response)

# 스트리밍 응답
for chunk in agent.stream("재택근무는 몇 일까지 가능한가요?"):
    print(chunk, end="", flush=True)

# 데이터 전송
flush_langfuse()
```

## Langfuse 설정

### 환경변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse Public Key | - |
| `LANGFUSE_SECRET_KEY` | Langfuse Secret Key | - |
| `LANGFUSE_HOST` | Langfuse 호스트 | `https://cloud.langfuse.com` |
| `LANGFUSE_SAMPLE_RATE` | 샘플링 비율 (0.0~1.0) | `1.0` |
| `LANGFUSE_ENABLE_MASKING` | PII 마스킹 활성화 | `false` |
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `DEFAULT_MODEL` | 기본 LLM 모델 | `gpt-5.2` |

### Self-hosted Langfuse

Docker로 로컬 Langfuse를 실행하려면:

```bash
# Langfuse 저장소 클론
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# 컨테이너 시작
docker compose up -d

# .env 파일 수정
LANGFUSE_HOST=http://localhost:3000
```

## 문제 해결

### Langfuse 연결 실패

```
RuntimeError: Langfuse가 초기화되지 않았습니다.
```

**해결:**

1. `.env` 파일에 Langfuse 키가 설정되어 있는지 확인
2. 키 형식 확인: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` 값이 올바른지 확인
3. Langfuse 대시보드에서 키가 활성화되어 있는지 확인

### 트레이스가 보이지 않음

```python
# flush() 호출 확인
from eval_agent import flush_langfuse
flush_langfuse()  # 스크립트 종료 전 필수
```

### 샘플링으로 인한 누락

```bash
# .env 파일에서 샘플링 비율 확인
LANGFUSE_SAMPLE_RATE=1.0  # 테스트 시 100%로 설정
```

### API 키 오류

```
AuthenticationError: Invalid API key
```

**해결:**

1. OpenAI API 키가 유효한지 확인
2. 키에 충분한 크레딧이 있는지 확인
3. `.env` 파일이 프로젝트 루트에 있는지 확인

## 참고 자료

- [Langfuse 공식 문서](https://langfuse.com/docs)
- [Langfuse Python SDK](https://langfuse.com/docs/sdk/python)
- [LangChain Callbacks](https://python.langchain.com/docs/concepts/callbacks/)
- [RAGAS 평가 프레임워크](https://docs.ragas.io/)

## 라이선스

MIT License

---

**AI 에이전트 개발 기술서** - 13장 "평가와 퀄리티" 실습 프로젝트
