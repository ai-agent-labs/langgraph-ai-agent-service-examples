import streamlit as st
from chatbot import create_chatbot_chain


def render():
    # 세션 상태 초기화
    if "ch06_session_id" not in st.session_state:
        st.session_state.ch06_session_id = "default"

    if "ch06_messages" not in st.session_state:
        st.session_state.ch06_messages = []

    # 사이드바 설정
    with st.sidebar:
        st.subheader("⚙️ 메모리 설정")

        memory_strategy = st.selectbox(
            "메모리 전략",
            ["Full History", "Window (최근 N개)"],
            help="Full History: 모든 대화 저장, Window: 최근 N개만 유지",
            key="ch06_strategy",
        )

        use_trimming = memory_strategy == "Window (최근 N개)"

        session_id = st.text_input(
            "Session ID",
            value=st.session_state.ch06_session_id,
            help="대화 세션을 구분하는 ID",
            key="ch06_session_input",
        )

        if session_id != st.session_state.ch06_session_id:
            st.session_state.ch06_session_id = session_id
            st.session_state.ch06_messages = []
            st.rerun()

        if st.button("🗑️ 대화 초기화", key="ch06_clear"):
            st.session_state.ch06_messages = []
            st.rerun()

        st.divider()
        st.markdown("""
        **메모리 전략:**
        - **Full History**: 완전한 맥락 유지
        - **Window**: 토큰 절약
        """)

        st.divider()
        st.markdown("""
        **예제 질문:**
        - "저는 개발팀 김철수입니다"
        - "연차 잔여일수 확인해주세요"
        - "제 이름이 뭐였죠?"
        """)

    # 대화 기록 표시
    for message in st.session_state.ch06_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("HR 관련 질문을 입력하세요...", key="ch06_input"):
        st.session_state.ch06_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            config = {"configurable": {"session_id": st.session_state.ch06_session_id}}

            try:
                chain = create_chatbot_chain(use_trimming=use_trimming)
                response = chain.invoke({"input": prompt}, config=config)
                full_response = response.text
                message_placeholder.markdown(full_response)

            except Exception as e:
                full_response = f"❌ 오류: {str(e)}"
                message_placeholder.error(full_response)

        st.session_state.ch06_messages.append(
            {"role": "assistant", "content": full_response}
        )
