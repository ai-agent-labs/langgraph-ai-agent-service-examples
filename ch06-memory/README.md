# 6장: 대화 메모리 챗봇

LangChain의 `RunnableWithMessageHistory`를 사용하여 대화 맥락을 유지하는 챗봇 예제입니다.

## 주요 기능

- **Full History 전략**: 모든 대화 기록을 저장하여 완전한 맥락 유지
- **Window 전략**: 최근 N개의 메시지만 유지하여 토큰 비용 절감
- **세션 관리**: session_id를 통한 독립적인 대화 세션 관리
- **Streamlit UI**: 직관적인 웹 인터페이스

## 실행 방법

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일에 OpenAI API 키 입력
OPENAI_API_KEY=sk-...
```

### 2. 의존성 설치

```bash
uv pip install -e .
```

### 3. 애플리케이션 실행

```bash
uv run streamlit run app.py
```

브라우저에서 http://localhost:8501 접속

## 핵심 코드 패턴

### 1. RunnableWithMessageHistory 기본 패턴

```python
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 세션별 대화 기록 저장소
chat_histories = {}

def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in chat_histories:
        chat_histories[session_id] = InMemoryChatMessageHistory()
    return chat_histories[session_id]

# 프롬프트와 모델
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 AI 어시스턴트입니다."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

model = init_chat_model(model_provider="openai", model="gpt-5.2")

# 메시지 히스토리가 포함된 체인
chain_with_history = RunnableWithMessageHistory(
    prompt | model,
    get_chat_history,
    input_messages_key="input",
    history_messages_key="history"
)

# 대화 실행
config = {"configurable": {"session_id": "user-123"}}
response = chain_with_history.invoke({"input": "안녕하세요"}, config=config)
```

### 2. Window 전략 (trim_messages)

```python
from langchain_core.messages import trim_messages

# 메시지 트리머 설정
trimmer = trim_messages(
    max_tokens=1000,
    strategy="last",
    token_counter=len,
    include_system=True,
    start_on="human"
)

# 트리밍을 포함한 체인
chain = (
    {"history": lambda x: trimmer.invoke(x["history"]), "input": lambda x: x["input"]}
    | prompt
    | model
)

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_chat_history,
    input_messages_key="input",
    history_messages_key="history"
)
```

### 3. Session ID 관리

```python
# 세션별 독립적인 대화
config_user1 = {"configurable": {"session_id": "user-1"}}
config_user2 = {"configurable": {"session_id": "user-2"}}

chain_with_history.invoke({"input": "내 이름은 철수야"}, config=config_user1)
chain_with_history.invoke({"input": "내 이름은 영희야"}, config=config_user2)
```

## 메모리 전략 비교

| 전략 | 토큰 사용량 | 정보 보존 | 적합한 상황 |
|------|-------------|----------|-------------|
| Full History | 높음 | 100% | 짧은 대화 (10회 이내) |
| Window | 중간 | 부분 | 중간 대화 (10~30회) |

## 학습 포인트

1. **RunnableWithMessageHistory**: LangChain의 대화 기록 관리 패턴
2. **InMemoryChatMessageHistory**: 메모리 내 대화 기록 저장소
3. **session_id**: 독립적인 대화 세션 구분
4. **trim_messages**: 최근 N개 메시지만 유지하여 토큰 절약
5. **MessagesPlaceholder**: 프롬프트에 대화 기록 삽입 위치 지정

## 관련 문서

- [LangChain RunnableWithMessageHistory](https://python.langchain.com/docs/how_to/message_history/)
- [LangChain ChatMessageHistory](https://python.langchain.com/docs/integrations/memory/)
