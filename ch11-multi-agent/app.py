import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from hr_team.supervisor import run_hr_team

st.set_page_config(page_title="HR 전문팀", page_icon="👥", layout="wide")
st.title("👥 HR 전문팀 시스템")
st.caption("Chapter 11: Supervisor 패턴 멀티 에이전트")

# 사이드바
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    ### Supervisor 패턴
    ```python
    workflow = StateGraph(SupervisorState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("leave_agent", leave_node)
    workflow.add_node("benefit_agent", benefit_node)
    workflow.add_conditional_edges("supervisor", router)
    ```

    **팀 구성:**
    - 🏖️ `leave_agent`: 휴가 전문
    - 🎁 `benefit_agent`: 복리후생
    - 👔 `supervisor`: 업무 조율
    """)

    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("AI 에이전트 개발 기술서 - 11장 예제")

st.markdown("""
**예제 질문:**
- "내 연차 확인해줘"
- "건강검진 신청은 어떻게 해?"
- "건강검진 신청하고 3월에 연차 3일 쓰고싶어"
""")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("HR 관련 요청을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("전문팀 협업 중..."):
            response = run_hr_team(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
