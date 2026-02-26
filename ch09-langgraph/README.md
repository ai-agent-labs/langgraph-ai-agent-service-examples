# Chapter 11: HR 요청 라우터 (LangGraph)

LangGraph의 StateGraph와 조건부 라우팅을 활용한 HR 요청 분류 시스템입니다.

## 핵심 기능

- **`StateGraph`**: 상태 기반 워크플로우 정의
- **조건부 라우팅**: 요청 유형에 따른 동적 분기
- **4가지 HR 카테고리**: leave, benefit, policy, onboarding

## HR 카테고리

| 카테고리 | 키워드 | 처리 내용 |
|---------|--------|----------|
| `leave` | 연차, 휴가, 근태 | 잔여 연차 확인, 휴가 신청 안내 |
| `benefit` | 건강검진, 교육비, 복지 | 복리후생 프로그램 안내 |
| `policy` | 재택, 규정, 정책 | 사내 정책 안내 |
| `onboarding` | 온보딩, 계정, 장비 | 신입사원 안내 |

## 그래프 구조

```
START → classify → [leave|benefit|policy|onboarding|general] → END
```

## 실행 방법

```bash
cd ch09-langgraph
cp .env.example .env

uv sync
uv run streamlit run app.py
```

## 예제 질문

- "내 연차 잔여일수가 얼마야?"
- "건강검진 신청은 어떻게 해?"
- "재택근무 정책 알려줘"
- "신입사원 IT 계정은 언제 발급돼?"

## 프로젝트 구조

```
ch09-langgraph/
├── src/hr_router/
│   ├── __init__.py
│   ├── config.py      # 설정 관리
│   ├── state.py       # HRRequestState 정의
│   ├── nodes.py       # 노드 함수들 (classify, handle_*)
│   └── graph.py       # StateGraph 구성
├── app.py             # Streamlit UI
└── pyproject.toml
```
