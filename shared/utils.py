import os
import streamlit as st


def init_session_state(defaults: dict):
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_chat_message(role: str, content: str):
    with st.chat_message(role):
        st.markdown(content)


def render_tool_call(tool_name: str, tool_input: dict, tool_output: str | None = None):
    with st.expander(f"🔧 도구 호출: {tool_name}", expanded=False):
        st.json(tool_input)
        if tool_output:
            st.markdown("**결과:**")
            st.code(tool_output)


def clear_chat_history(key: str = "messages"):
    if key in st.session_state:
        st.session_state[key] = []


def get_env_status() -> dict:
    return {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "LANGFUSE_PUBLIC_KEY": bool(os.getenv("LANGFUSE_PUBLIC_KEY")),
        "OPENSEARCH_HOST": bool(os.getenv("OPENSEARCH_HOST")),
    }


def render_env_warning():
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return False
    return True
