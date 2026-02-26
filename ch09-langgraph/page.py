import streamlit as st
from hr_router.graph import run_hr_router


def render():
    # 세션 상태 초기화
    if "ch09_messages" not in st.session_state:
        st.session_state.ch09_messages = []

    # 사이드바 정보
    with st.sidebar:
        st.subheader("🔀 HR 카테고리")
        st.markdown("""
        - 🏖️ **leave**: 휴가, 연차, 근태
        - 🎁 **benefit**: 건강검진, 교육비, 복지
        - 📋 **policy**: 재택근무, 규정
        - 🆕 **onboarding**: 입사, 계정, 장비
        """)

        st.divider()
        st.markdown("""
        **예제 질문:**
        - "내 연차 잔여일수가 얼마야?"
        - "건강검진 신청은 어떻게 해?"
        - "재택근무 정책 알려줘"
        """)

        if st.button("🗑️ 대화 초기화", key="ch09_clear"):
            st.session_state.ch09_messages = []
            st.rerun()

    # 대화 기록 표시
    for message in st.session_state.ch09_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "category" in message:
                st.caption(f"분류: `{message['category']}`")

    # 사용자 입력
    if prompt := st.chat_input("HR 관련 질문을 입력하세요...", key="ch09_input"):
        st.session_state.ch09_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("요청 분류 중..."):
                try:
                    result = run_hr_router(prompt)
                    st.markdown(result["response"])
                    st.caption(f"분류: `{result['category']}`")
                    response = result["response"]
                    category = result["category"]
                except Exception as e:
                    response = f"❌ 오류: {str(e)}"
                    category = "error"
                    st.error(response)

        st.session_state.ch09_messages.append({
            "role": "assistant",
            "content": response,
            "category": category,
        })
