# Chapter 9: HR 정책 어시스턴트 + 도구

LangChain의 도구 호출(Tool Calling) 기능을 활용한 HR 어시스턴트 예제입니다.

## 핵심 기능

- **`@tool` 데코레이터**: 함수를 LLM 도구로 변환
- **`bind_tools()`**: 모델에 도구 바인딩
- **도구 실행 흐름**: LLM → Tool Call → Tool Result → Final Answer

## HR 도구

| 도구 | 설명 |
|------|------|
| `check_leave_balance` | 직원 연차 잔여일수 조회 |
| `search_policy` | HR 정책 키워드 검색 |
| `submit_leave_request` | 휴가 신청 제출 |

## 실행 방법

```bash
cd ch07-tool-mcp
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 설정

uv sync
uv run streamlit run app.py
```

## 예제 질문

- "EMP001의 연차 잔여일수 알려줘"
- "재택근무 정책이 어떻게 돼?"
- "교육비 지원 정책 검색해줘"
- "EMP001이 12월 23일부터 25일까지 연차 신청할게"

## 프로젝트 구조

```
ch07-tool-mcp/
├── src/hr_assistant/
│   ├── __init__.py
│   ├── config.py      # 설정 관리
│   ├── data.py        # Mock HR 데이터
│   ├── tools.py       # 3가지 HR 도구
│   └── chain.py       # LLM + 도구 통합
├── app.py             # Streamlit UI
└── pyproject.toml
```
