from langgraph.graph import StateGraph, START, END

from hr_router.state import HRRequestState
from hr_router.nodes import (
    classify_node,
    route_query,
    leave_node,
    benefit_node,
    policy_node,
    onboarding_node,
    general_node,
)


def create_hr_router() -> StateGraph:
    graph = StateGraph(HRRequestState)

    graph.add_node("classify", classify_node)
    graph.add_node("leave", leave_node)
    graph.add_node("benefit", benefit_node)
    graph.add_node("policy", policy_node)
    graph.add_node("onboarding", onboarding_node)
    graph.add_node("general", general_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_query,
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
