"""HR 멀티 에이전트 시스템 (Supervisor 패턴).

``langgraph_supervisor.create_supervisor`` 팩토리를 사용해 Supervisor
라우팅 로직(도구 기반 handoff)과 에이전트 그래프 구성을 한 번에 만든다.
``StateGraph``를 직접 조립하는 것보다 훨씬 간결하다.
"""

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph_supervisor import create_supervisor

from hr_team.agents import create_benefit_agent, create_leave_agent
from hr_team.config import get_settings

SUPERVISOR_PROMPT = """당신은 HR 상담용 멀티 에이전트 시스템의 조정자입니다.

- 직원 질문을 읽고, 연차 / 복리후생 중 어떤 에이전트가 적합한지 판단합니다.
- 필요하면 에이전트에게 작업을 맡기고, 그 결과를 읽고 다음 액션을 정합니다.
- 직원이 이해하기 쉬운 하나의 최종 답변만 전달합니다.
- 어떤 에이전트도 적합하지 않으면, 'HR 담당자가 도와드리겠습니다.' 라고 답합니다."""


def create_hr_supervisor():
    """HR Supervisor 그래프 생성.

    도메인 에이전트 2개(leave, benefit) + 슈퍼바이저 1개 구성.
    ``create_supervisor``가 handoff 도구를 자동으로 생성하여 에이전트 간
    위임을 처리한다.
    """
    settings = get_settings()
    model = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=settings.temperature,
    )

    leave_agent = create_leave_agent()
    benefit_agent = create_benefit_agent()

    agents = [leave_agent, benefit_agent]
    supervisor = create_supervisor(
        agents=agents,
        model=model,
        prompt=SUPERVISOR_PROMPT,
    )

    return supervisor.compile()


def run_hr_team(query: str) -> str:
    """HR 팀 실행."""
    supervisor = create_hr_supervisor()
    result = supervisor.invoke({"messages": [HumanMessage(content=query)]})

    if result["messages"]:
        return result["messages"][-1].content

    return "요청을 처리할 수 없습니다."
