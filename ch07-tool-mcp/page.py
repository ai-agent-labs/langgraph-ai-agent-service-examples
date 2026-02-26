import streamlit as st
from hr_assistant.chain import chat_with_tools


def render():
    # 세션 상태 초기화
    if "ch07_messages" not in st.session_state:
        st.session_state.ch07_messages = []

    # 사이드바 정보
    with st.sidebar:
        st.subheader("🔧 사용 가능한 도구")
        st.markdown("""
        - `check_leave_balance`: 연차 잔여일수 조회
        - `search_policy`: HR 정책 검색
        - `submit_leave_request`: 휴가 신청
        """)

        st.divider()
        st.markdown("""
        **예제 질문:**
        - "EMP001의 연차 잔여일수 알려줘"
        - "재택근무 정책이 어떻게 돼?"
        - "12월 23일부터 25일까지 연차 신청"
        """)

        if st.button("🗑️ 대화 초기화", key="ch07_clear"):
            st.session_state.ch07_messages = []
            st.rerun()

    # 대화 기록 표시
    for message in st.session_state.ch07_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요...", key="ch07_input"):
        st.session_state.ch07_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("도구 호출 중..."):
                try:
                    response = chat_with_tools(prompt)
                    st.markdown(response)
                except Exception as e:
                    response = f"❌ 오류: {str(e)}"
                    st.error(response)

        st.session_state.ch07_messages.append(
            {"role": "assistant", "content": response}
        )
