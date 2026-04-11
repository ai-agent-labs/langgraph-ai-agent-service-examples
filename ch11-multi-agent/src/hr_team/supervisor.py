"""
HR 멀티 에이전트 시스템 (Supervisor 패턴).

책 11.4절의 권장 구현 방식인 ``langgraph_supervisor.create_supervisor``를
사용한다. 이 팩토리는 Supervisor 라우팅 로직(도구 기반 handoff)과 에이전트
그래프 구성을 한 번에 만들어 주므로, ``StateGraph``를 직접 조립하던 이전
구현보다 훨씬 간결하다.
"""

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph_supervisor import create_supervisor

from hr_team.agents import create_benefit_agent, create_leave_agent
from hr_team.config import get_settings

SUPERVISOR_PROMPT = """당신은 HR 팀의 수퍼바이저입니다.
직원의 요청을 분석하여 적절한 전문 에이전트를 선택하세요.

팀 구성:
- leave_agent: 휴가/연차 관련 (잔여 연차, 휴가 신청)
- benefit_agent: 복리후생 관련 (건강검진, 교육비, 통신비)

요청을 읽고 가장 적합한 에이전트에 작업을 위임하세요.
복합 요청의 경우 여러 에이전트를 순차적으로 호출하고, 모두 처리되면
최종 응답을 한 번에 사용자에게 전달하세요."""


def create_hr_supervisor():
    """HR Supervisor 그래프 생성.

    책 11.4절: 도메인 에이전트 2개(leave, benefit) + 슈퍼바이저 1개.
    ``langgraph_supervisor.create_supervisor``가 handoff 도구를 자동으로
    생성하여 에이전트 간 위임을 처리한다.
    """
    settings = get_settings()
    model = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=settings.temperature,
    )

    leave_agent = create_leave_agent()
    benefit_agent = create_benefit_agent()

    supervisor = create_supervisor(
        model=model,
        agents=[leave_agent, benefit_agent],
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
