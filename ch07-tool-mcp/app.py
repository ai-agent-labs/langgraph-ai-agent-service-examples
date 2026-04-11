import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from hr_assistant.chain import chat_with_tools

st.set_page_config(page_title="HR 정책 어시스턴트", page_icon="👔", layout="wide")
st.title("👔 HR 정책 어시스턴트")
st.caption("Chapter 7: 도구 호출 (Tool Calling)")

# 사이드바
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    ### Tool Calling
    ```python
    @tool
    def check_leave_balance(emp_id: str):
        '''연차 잔여일수 조회'''
        ...

    llm_with_tools = llm.bind_tools(tools)
    ```

    **사용 가능한 도구:**
    - ✅ 연차 잔여일수 조회
    - ✅ HR 정책 검색
    - ✅ 휴가 신청
    """)

    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("AI 에이전트 개발 기술서 - 7장 예제")

st.markdown("""
**예제 질문:**
- "EMP001의 연차 잔여일수 알려줘"
- "재택근무 정책이 어떻게 돼?"
- "EMP001이 12월 23일부터 25일까지 연차 신청할게"
""")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("도구 호출 중..."):
            response = chat_with_tools(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
