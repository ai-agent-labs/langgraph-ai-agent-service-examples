import streamlit as st
from hr_team.supervisor import run_hr_team


def render():
    # 세션 상태 초기화
    if "ch11_messages" not in st.session_state:
        st.session_state.ch11_messages = []

    # 사이드바 정보
    with st.sidebar:
        st.subheader("👥 팀 구성")
        st.markdown("""
        - 🏖️ **leave_agent**: 휴가/연차 전문
        - 🎁 **benefit_agent**: 복리후생 전문
        - 📋 **policy_agent**: 정책/규정 전문
        - 👔 **supervisor**: 업무 조율
        """)

        st.divider()
        st.markdown("""
        **복합 요청 예제:**
        - "건강검진 신청하고 3월에 연차 3일 쓰고싶어"
        """)

        if st.button("🗑️ 대화 초기화", key="ch11_clear"):
            st.session_state.ch11_messages = []
            st.rerun()

    # 대화 기록 표시
    for message in st.session_state.ch11_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("HR 관련 요청을 입력하세요...", key="ch11_input"):
        st.session_state.ch11_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("전문팀 협업 중..."):
                try:
                    response = run_hr_team(prompt)
                    st.markdown(response)
                except Exception as e:
                    response = f"❌ 오류: {str(e)}"
                    st.error(response)

        st.session_state.ch11_messages.append(
            {"role": "assistant", "content": response}
        )
