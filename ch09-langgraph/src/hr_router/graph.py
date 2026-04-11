from langgraph.graph import END, START, StateGraph

from hr_router.nodes import (
    classify_request,
    handle_benefit,
    handle_general,
    handle_leave,
    handle_onboarding,
    handle_policy,
    route_by_category,
)
from hr_router.state import HRRequestState


def create_hr_router() -> StateGraph:
    graph = StateGraph(HRRequestState)

    # 노드 추가
    graph.add_node("classify", classify_request)
    graph.add_node("leave", handle_leave)
    graph.add_node("benefit", handle_benefit)
    graph.add_node("policy", handle_policy)
    graph.add_node("onboarding", handle_onboarding)
    graph.add_node("general", handle_general)

    # 연결: START -> classify -> 조건부 분기 -> 각 처리 경로 -> END
    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_by_category,
        {
            "leave": "leave",
            "benefit": "benefit",
            "policy": "policy",
            "onboarding": "onboarding",
            "general": "general",
        },
    )
    graph.add_edge("leave", END)
    graph.add_edge("benefit", END)
    graph.add_edge("policy", END)
    graph.add_edge("onboarding", END)
    graph.add_edge("general", END)

    return graph.compile()


def run_hr_router(query: str) -> dict:
    router = create_hr_router()
    result = router.invoke({"query": query, "category": "", "response": ""})
    return result
