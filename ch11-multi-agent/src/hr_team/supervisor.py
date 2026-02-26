from typing import Literal, TypedDict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from hr_team.config import get_settings
from hr_team.agents import create_leave_agent, create_benefit_agent, create_policy_agent


class SupervisorState(TypedDict):
    """Supervisor 상태"""
    messages: list
    next_agent: str


SUPERVISOR_PROMPT = """당신은 HR 팀의 수퍼바이저입니다.
직원의 요청을 분석하여 적절한 전문 에이전트를 선택하세요.

팀 구성:
- leave_agent: 휴가/연차 관련 (잔여 연차, 휴가 신청)
- benefit_agent: 복리후생 관련 (건강검진, 교육비, 통신비)
- policy_agent: 정책/규정 관련 (재택근무, 야근)

요청을 읽고 가장 적합한 에이전트 이름을 선택하세요.
복합 요청의 경우 가장 중요한 부분을 처리할 에이전트를 선택하세요."""


def create_supervisor_node(model):
    """슈퍼바이저 노드 생성"""

    # 구조화된 출력으로 next_agent 선택
    class RouterDecision(TypedDict):
        """라우터 결정"""
        next_agent: Literal["leave_agent", "benefit_agent", "policy_agent"]

    supervisor_chain = (
        model.with_structured_output(RouterDecision)
    )

    def supervisor(state: SupervisorState) -> SupervisorState:
        """슈퍼바이저: 다음 에이전트 결정"""
        messages = state["messages"]

        # 시스템 프롬프트 + 사용자 메시지
        full_messages = [
            {"role": "system", "content": SUPERVISOR_PROMPT},
            *messages
        ]

        result = supervisor_chain.invoke(full_messages)
        return {"next_agent": result["next_agent"]}

    return supervisor


def create_agent_node(agent, name: str):
    """에이전트 노드 생성"""
    def agent_node(state: SupervisorState):
        """에이전트 실행"""
        result = agent.invoke(state)
        return {"messages": result["messages"]}

    return agent_node


def route_to_agent(state: SupervisorState) -> str:
    """다음 에이전트로 라우팅"""
    return state.get("next_agent", "leave_agent")


def create_hr_supervisor():
    """HR Supervisor 그래프 생성"""
    settings = get_settings()
    model = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=settings.temperature,
    )

    # 에이전트 생성
    leave_agent = create_leave_agent()
    benefit_agent = create_benefit_agent()
    policy_agent = create_policy_agent()

    # 그래프 구성
    workflow = StateGraph(SupervisorState)

    # 노드 추가
    workflow.add_node("supervisor", create_supervisor_node(model))
    workflow.add_node("leave_agent", create_agent_node(leave_agent, "leave_agent"))
    workflow.add_node("benefit_agent", create_agent_node(benefit_agent, "benefit_agent"))
    workflow.add_node("policy_agent", create_agent_node(policy_agent, "policy_agent"))

    # 엣지 추가
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "leave_agent": "leave_agent",
            "benefit_agent": "benefit_agent",
            "policy_agent": "policy_agent",
        }
    )
    workflow.add_edge("leave_agent", END)
    workflow.add_edge("benefit_agent", END)
    workflow.add_edge("policy_agent", END)

    return workflow.compile()


def run_hr_team(query: str) -> str:
    """HR 팀 실행"""
    supervisor = create_hr_supervisor()
    result = supervisor.invoke({"messages": [HumanMessage(content=query)]})

    if result["messages"]:
        return result["messages"][-1].content

    return "요청을 처리할 수 없습니다."
