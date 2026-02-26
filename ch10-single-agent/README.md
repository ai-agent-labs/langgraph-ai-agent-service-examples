# Chapter 10: HR 자율 에이전트 (ReAct 패턴)

LangChain의 `create_agent`를 활용한 자율 HR 에이전트입니다.

## 핵심 기능

- **ReAct 패턴**: Reason-Act-Observe 반복
- **자율적 도구 선택**: LLM이 상황에 맞는 도구를 스스로 선택
- **다단계 추론**: 복잡한 요청을 여러 단계로 분해하여 처리

## Ch11과의 차이점

| 구분 | Ch10 (단일 에이전트) | Ch11 (멀티 에이전트) |
|------|---------------------|---------------------|
| 에이전트 수 | 1개 | 4개 (supervisor + 3 전문가) |
| 도구 관리 | 모든 도구를 1개가 보유 | 역할별로 분산 |
| 복잡한 요청 | 한 에이전트가 전담 | 전문가 협업 |

## ReAct 동작 예시

```
사용자: "12월에 3일 연차 가능한지 확인하고 신청해줘"

1. [Reason] 먼저 잔여 연차를 확인해야겠다
2. [Act] check_leave_balance(employee_id="EMP001")
3. [Observe] 잔여 연차 12일 확인
4. [Reason] 12일이면 3일 사용 가능하다
5. [Act] submit_leave_request(start_date="2024-12-23", days=3)
6. [Observe] 신청 완료 (신청번호: REQ-2024-001)
7. [Final] "잔여 연차가 12일이므로 3일 사용 가능합니다..."
```

## 실행 방법

```bash
cd ch10-single-agent
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 설정

uv sync
uv run streamlit run app.py
```

## 예제 질문

- "EMP001의 연차 확인해줘"
- "12월에 3일 연차 가능한지 확인하고 신청해줘"
- "재택근무 정책이랑 내 연차 잔여일수 알려줘"

## 프로젝트 구조

```
ch10-single-agent/
├── src/hr_agent/
│   ├── __init__.py
│   ├── config.py      # 설정 관리
│   ├── tools.py       # HR 도구 (check, submit, search)
│   └── agent.py       # ReAct 에이전트 생성
├── app.py             # Streamlit UI
└── pyproject.toml
```
