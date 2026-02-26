import streamlit as st

CHAPTERS = {
    "기초": {
        "icon": "📚",
        "chapters": [
            {"id": "ch02", "dir": "ch02-getting-started", "name": "개발 시작하기", "desc": "첫 AI 에이전트"},
            {"id": "ch03", "dir": "ch03-langchain-basics", "name": "LCEL 기본 체인", "desc": "LangChain Expression Language"},
            {"id": "ch06", "dir": "ch06-memory", "name": "대화 메모리", "desc": "RunnableWithMessageHistory"},
            {"id": "ch08", "dir": "ch08-structured-output", "name": "구조화된 출력", "desc": "Pydantic + with_structured_output"},
        ],
    },
    "도구와 워크플로우": {
        "icon": "🔧",
        "chapters": [
            {"id": "ch07", "dir": "ch07-tool-mcp", "name": "도구 호출", "desc": "@tool + bind_tools"},
            {"id": "ch09", "dir": "ch09-langgraph", "name": "LangGraph 라우팅", "desc": "StateGraph 조건부 분기"},
        ],
    },
    "에이전트와 고급": {
        "icon": "🤖",
        "chapters": [
            {"id": "ch10", "dir": "ch10-single-agent", "name": "단일 에이전트", "desc": "ReAct 패턴"},
            {"id": "ch11", "dir": "ch11-multi-agent", "name": "멀티에이전트", "desc": "Supervisor 패턴"},
            {"id": "ch05", "dir": "ch05-rag", "name": "RAG 검색", "desc": "하이브리드 검색 + 리랭킹"},
            {"id": "ch13", "dir": "ch13-evaluation", "name": "평가 & 모니터링", "desc": "Langfuse 트레이싱"},
        ],
    },
}


def render_sidebar() -> str | None:
    with st.sidebar:
        st.title("🤖 AI 에이전트 실습")
        st.caption("LangChain & LangGraph 기술서")
        st.divider()

        selected = None

        for part_name, part_info in CHAPTERS.items():
            st.subheader(f"{part_info['icon']} {part_name}")

            for chapter in part_info["chapters"]:
                if st.button(
                    f"**{chapter['id'].upper()}**: {chapter['name']}",
                    key=f"nav_{chapter['id']}",
                    help=chapter["desc"],
                    use_container_width=True,
                ):
                    selected = chapter["id"]
                    st.session_state.current_chapter = chapter["id"]

            st.write("")

        st.divider()
        st.caption("© 2025 AI Agent Book")

        if selected:
            return selected
        return st.session_state.get("current_chapter")


def get_chapter_info(chapter_id: str) -> dict | None:
    for part_info in CHAPTERS.values():
        for chapter in part_info["chapters"]:
            if chapter["id"] == chapter_id:
                return chapter
    return None
