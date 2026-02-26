import streamlit as st
from hr_agent.agent import run_hr_agent


def render():
    # 세션 상태 초기화
    if "ch10_messages" not in st.session_state:
        st.session_state.ch10_messages = []

    # 사이드바 정보
    with st.sidebar:
        st.subheader("🤖 ReAct 패턴")
        st.markdown("""
        1. 🤔 **Reason**: 사용자 요청 분석
        2. ⚡ **Act**: 필요한 도구 호출
        3. 👀 **Observe**: 결과 확인
        4. 🔄 반복 후 최종 응답
        """)

        st.divider()
        st.markdown("""
        **예제 질문:**
        - "EMP001의 연차 확인해줘"
        - "12월에 3일 연차 가능한지 확인하고 신청해줘"
        """)

        if st.button("🗑️ 대화 초기화", key="ch10_clear"):
            st.session_state.ch10_messages = []
            st.rerun()

    # 대화 기록 표시
    for message in st.session_state.ch10_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("HR 관련 요청을 입력하세요...", key="ch10_input"):
        st.session_state.ch10_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("ReAct 루프 실행 중..."):
                try:
                    response = run_hr_agent(prompt)
                    st.markdown(response)
                except Exception as e:
                    response = f"❌ 오류: {str(e)}"
                    st.error(response)

        st.session_state.ch10_messages.append(
            {"role": "assistant", "content": response}
        )
