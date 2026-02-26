import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from hr_agent.agent import run_hr_agent

st.set_page_config(page_title="HR 자율 에이전트", page_icon="🤖", layout="wide")
st.title("🤖 HR 자율 에이전트")
st.caption("Chapter 10: ReAct 패턴 단일 에이전트")

# 사이드바
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    ### ReAct 패턴
    ```python
    agent = create_agent(
        model,
        tools,
        system_prompt
    )
    ```

    **동작 방식:**
    1. 🤔 **Reason**: 요청 분석
    2. ⚡ **Act**: 도구 호출
    3. 👀 **Observe**: 결과 확인
    4. 🔄 반복 후 최종 응답
    """)

    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("AI 에이전트 개발 기술서 - 10장 예제")

st.markdown("""
**예제 질문:**
- "EMP001의 연차 확인해줘"
- "12월에 3일 연차 가능한지 확인하고 신청해줘"
- "재택근무 정책이랑 내 연차 잔여일수 알려줘"
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
        with st.spinner("ReAct 루프 실행 중..."):
            response = run_hr_agent(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
