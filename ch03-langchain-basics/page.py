import streamlit as st
from qa_chatbot.chain import create_qa_chain, stream_qa


def render():
    # 세션 상태 초기화
    if "ch03_chain" not in st.session_state:
        with st.spinner("챗봇 초기화 중..."):
            st.session_state.ch03_chain = create_qa_chain()

    if "ch03_messages" not in st.session_state:
        st.session_state.ch03_messages = []

    # 사이드바 정보
    with st.sidebar:
        st.markdown("""
        ### LCEL 파이프라인
        ```python
        chain = prompt | model | output_parser
        ```

        **주요 기능:**
        - 실시간 스트리밍 응답
        - `.invoke()` / `.stream()` 메서드
        """)

        if st.button("🗑️ 대화 초기화", key="ch03_clear"):
            st.session_state.ch03_messages = []
            st.rerun()

    # 대화 기록 표시
    for message in st.session_state.ch03_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요", key="ch03_input"):
        st.session_state.ch03_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                for chunk in stream_qa(prompt, st.session_state.ch03_chain):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")

                response_placeholder.markdown(full_response)
                st.session_state.ch03_messages.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                error_message = f"오류: {str(e)}"
                response_placeholder.error(error_message)
