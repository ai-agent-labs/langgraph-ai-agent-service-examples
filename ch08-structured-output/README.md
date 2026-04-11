# 8장: 구조화된 출력 - 정보 추출기

LangChain `with_structured_output`을 활용한 구조화된 정보 추출 예제입니다.

## 📋 주요 기능

- ✅ **Pydantic 스키마**: `BaseModel` 기반 데이터 구조 정의
- ✅ **with_structured_output**: LLM 출력을 스키마에 맞게 자동 변환
- ✅ **타입 안전성**: Pydantic 자동 검증
- ✅ **실용 예제**: 연락처, 영화 정보 추출

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
uv pip install -e .
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

### 3. 애플리케이션 실행

```bash
uv run streamlit run app.py
```

## 📁 프로젝트 구조

```
ch08-structured-output/
├── src/info_extractor/
│   ├── schemas.py       # Pydantic 스키마 정의
│   └── extractor.py     # 정보 추출 로직
├── app.py               # Streamlit 애플리케이션
└── README.md
```

## 💡 핵심 코드 패턴

### Pydantic 스키마 정의 (책 8.2-5절)

```python
from pydantic import BaseModel, Field


class LeaveRequest(BaseModel):
    """휴가 신청 정보를 추출한 결과입니다."""

    employee_id: str = Field(description="직원 ID. 예: EMP001, EMP002")
    leave_type: str = Field(
        description="휴가 유형. 연차, 반차, 병가, 경조사 중 하나를 선택합니다."
    )
    start_date: str = Field(description="휴가 시작일. YYYY-MM-DD 형식으로 작성합니다.")
    end_date: str = Field(description="휴가 종료일. YYYY-MM-DD 형식으로 작성합니다.")
    reason: str = Field(description="휴가 사유를 간단히 요약합니다.")
```

### 구조화된 출력 사용

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5.2", model_provider="openai")
structured_llm = model.with_structured_output(LeaveRequest)

result = structured_llm.invoke(
    "EMP001 직원이 12월 23일부터 25일까지 경조사 휴가 신청합니다."
)
print(result.employee_id)   # "EMP001"
print(result.leave_type)    # "경조사"
print(result.start_date)    # "2024-12-23"
```

## 🔗 관련 챕터

- **Ch3: LangChain 기초** - LCEL 파이프라인
- **Ch9: LangGraph** - 워크플로우 자동화로 확장
- **Ch10: 단일 에이전트** - 도구로 활용

## 📚 참고 자료

- [Structured Output 공식 문서](https://python.langchain.com/docs/how_to/structured_output/)
- [Pydantic 문서](https://docs.pydantic.dev/)

## 📝 라이선스

MIT License
