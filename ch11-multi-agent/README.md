# Chapter 11: HR 전문팀 시스템 (Supervisor 패턴)

LangGraph의 Supervisor 패턴을 활용한 멀티 에이전트 HR 시스템입니다.

## 핵심 기능

- **Supervisor 패턴**: 중앙 조율자가 업무를 분배
- **전문화된 에이전트**: 각 분야별 전문 에이전트
- **협업 처리**: 복합 요청을 여러 에이전트가 순차 처리

## Ch10과의 차이점

| 구분 | Ch10 (단일 에이전트) | Ch11 (멀티 에이전트) |
|------|---------------------|---------------------|
| 에이전트 수 | 1개 | 4개 (supervisor + 3 전문가) |
| 도구 관리 | 모든 도구를 1개가 보유 | 역할별로 분산 |
| 복잡한 요청 | 한 에이전트가 전담 | 전문가 협업 |
| 확장성 | 도구 증가 시 복잡 | 에이전트 추가로 확장 |

## 팀 구성

| 에이전트 | 역할 | 도구 |
|---------|------|------|
| `supervisor` | 요청 분석 및 위임 | - |
| `leave_agent` | 휴가/연차 담당 | get_leave_balance, request_leave |
| `benefit_agent` | 복리후생 담당 | get_benefit_info, apply_benefit |
| `policy_agent` | 정책/규정 담당 | search_policy |

## 동작 흐름

```
사용자 → Supervisor → [분석] → 적절한 에이전트 선택
                            ↓
         leave_agent ← "연차 관련"
         benefit_agent ← "복지 관련"
         policy_agent ← "정책 관련"
                            ↓
         결과 통합 ← Supervisor → 최종 응답
```

## 실행 방법

```bash
cd ch11-multi-agent
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 설정

uv sync
uv run streamlit run app.py
```

## 예제 질문

**단일 분야:**

- "내 연차 확인해줘" → leave_agent
- "건강검진 신청은 어떻게 해?" → benefit_agent
- "재택근무 정책 알려줘" → policy_agent

**복합 요청:**

- "건강검진 신청하고 3월에 연차 3일 쓰고싶어" → benefit_agent + leave_agent

## 프로젝트 구조

```
ch11-multi-agent/
├── src/hr_team/
│   ├── __init__.py
│   ├── config.py      # 설정 관리
│   ├── tools.py       # 분야별 도구
│   ├── agents.py      # 전문 에이전트들
│   └── supervisor.py  # Supervisor 구성
├── app.py             # Streamlit UI
└── pyproject.toml
```
