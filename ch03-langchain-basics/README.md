# Ch3: LangChain 기초 - Q&A 챗봇

LangChain LCEL(LangChain Expression Language)을 활용한 기본 질의응답 챗봇 예제입니다.

## 📋 주요 기능

- ✅ **LCEL 파이프라인**: `prompt | model | output_parser` 구조
- ✅ **최신 LangChain 1.1.x**: `init_chat_model` 사용
- ✅ **스트리밍 응답**: `.stream()` 메서드로 실시간 응답
- ✅ **간단한 UI**: Streamlit 기반 웹 인터페이스

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 pip 사용
pip install -e .
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 OPENAI_API_KEY 설정
```

### 3. 애플리케이션 실행

```bash
# Streamlit 앱 실행
uv run streamlit run app.py

# 또는
streamlit run app.py
```

## 📁 프로젝트 구조

```
ch03-langchain-basics/
├── src/qa_chatbot/
│   ├── __init__.py      # 패키지 초기화
│   ├── config.py        # 설정 관리 (pydantic-settings)
│   ├── prompts.py       # 프롬프트 템플릿
│   └── chain.py         # LCEL 체인 구현
├── app.py               # Streamlit 웹 애플리케이션
├── pyproject.toml       # 프로젝트 설정
├── .env.example         # 환경 변수 예제
└── README.md
```

## 💡 핵심 코드 패턴

### 1. 기본 LCEL 체인 구성

```python
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = init_chat_model("gpt-5.2", model_provider="openai")

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 Q&A 어시스턴트입니다."),
    ("user", "{question}")
])

chain = prompt | model | StrOutputParser()

result = chain.invoke({"question": "Python이란 무엇인가요?"})
```

### 2. 스트리밍 응답

```python
for chunk in chain.stream({"question": "AI에 대해 설명해주세요"}):
    print(chunk, end="", flush=True)
```

### 3. RunnableLambda를 활용한 후처리

```python
from langchain_core.runnables import RunnableLambda

def add_ai_indicator(message):
    message.content += "\n\n(이 응답은 AI에 의해 생성되었습니다.)"
    return message

chain = prompt | model | RunnableLambda(add_ai_indicator) | StrOutputParser()
```

### 4. RunnableParallel을 활용한 병렬 처리

```python
from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import PromptTemplate

pros_chain = PromptTemplate.from_template("{subject}의 장점") | model
cons_chain = PromptTemplate.from_template("{subject}의 단점") | model

parallel_chain = RunnableParallel(pros=pros_chain, cons=cons_chain)
result = parallel_chain.invoke({"subject": "AI"})
```

## 🔗 관련 챕터

- **Ch6: 메모리** - 대화 기록 관리로 확장
- **Ch7: 도구/MCP** - 외부 도구 통합
- **Ch8: 구조화된 출력** - Pydantic 모델로 출력 구조화

## 📚 참고 자료

- [LangChain LCEL 공식 문서](https://python.langchain.com/docs/expression_language/)
- [init_chat_model 가이드](https://python.langchain.com/docs/how_to/chat_models_universal_init/)
- [Streamlit 문서](https://docs.streamlit.io/)

## ⚙️ 개발 도구

```bash
# 코드 포맷팅
uv run ruff format .

# 린팅
uv run ruff check .

# 타입 체크
uv run mypy src/
```

## 📝 라이선스

MIT License
