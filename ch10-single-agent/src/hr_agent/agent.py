from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from hr_agent.config import get_settings
from hr_agent.tools import HR_TOOLS

SYSTEM_PROMPT = """당신은 HR 전문 어시스턴트입니다.
직원의 요청을 분석하고 적절한 도구를 사용하여 처리하세요.

사용 가능한 도구:
- check_leave_balance: 연차 잔여일수 조회
- submit_leave_request: 휴가 신청
- search_policy: HR 정책 검색

ReAct 패턴으로 동작합니다:
1. 사용자 요청 분석 (Reason)
2. 필요한 도구 호출 (Act)
3. 결과 확인 (Observe)
4. 다음 행동 결정 (Reason) - 반복

모든 응답은 한국어로 친절하게 제공하세요."""


def create_hr_agent():
    settings = get_settings()
    model = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=settings.temperature,
    )

    agent = create_agent(
        model=model,
        tools=HR_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


def run_hr_agent(query: str) -> str:
    agent = create_hr_agent()
    result = agent.invoke({"messages": [("user", query)]})

    if result["messages"]:
        return result["messages"][-1].text

    return "요청을 처리할 수 없습니다."
