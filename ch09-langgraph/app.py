import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from hr_router.graph import run_hr_router

st.set_page_config(page_title="HR 요청 라우터", page_icon="🔀", layout="wide")
st.title("🔀 HR 요청 라우터")
st.caption("Chapter 11: LangGraph 조건부 라우팅")

# 사이드바
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    ### 조건부 라우팅
    ```python
    def route_by_category(state):
        category = state["category"]
        return category

    graph.add_conditional_edges(
        "classify",
        route_by_category,
        {...}
    )
    ```

    **HR 카테고리:**
    - 🏖️ `leave`: 휴가, 연차
    - 🎁 `benefit`: 복리후생
    - 📋 `policy`: 정책, 규정
    - 🆕 `onboarding`: 입사, 장비
    """)

    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("AI 에이전트 개발 기술서 - 11장 예제")

st.markdown("""
**예제 질문:**
- "내 연차 잔여일수가 얼마야?"
- "건강검진 신청은 어떻게 해?"
- "재택근무 정책 알려줘"
- "신입사원 IT 계정은 언제 발급돼?"
""")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "category" in message:
            st.caption(f"분류된 카테고리: `{message['category']}`")

if prompt := st.chat_input("HR 관련 질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("요청 분류 중..."):
            result = run_hr_router(prompt)
        st.markdown(result["response"])
        st.caption(f"분류된 카테고리: `{result['category']}`")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "category": result["category"],
    })
