"""
Q&A 챗봇 Streamlit 애플리케이션

간단한 질의응답 인터페이스를 제공합니다.
"""

import streamlit as st

from qa_chatbot.chain import create_qa_chain, stream_qa

# 페이지 설정
st.set_page_config(
    page_title="Q&A 챗봇",
    page_icon="💬",
    layout="centered",
)

st.title("💬 Q&A 챗봇")
st.caption("🚀 LangChain LCEL 기반 질의응답 시스템")

# 세션 상태 초기화
if "chain" not in st.session_state:
    with st.spinner("챗봇 초기화 중..."):
        st.session_state.chain = create_qa_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("질문을 입력하세요"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성 (스트리밍)
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            for chunk in stream_qa(prompt, st.session_state.chain):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_message = f"오류가 발생했습니다: {str(e)}"
            response_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# 사이드바
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    ### LangChain LCEL 체인

    이 챗봇은 다음 LCEL 파이프라인을 사용합니다:

    ```python
    chain = prompt | model | output_parser
    ```

    **주요 기능:**
    - ✅ 실시간 스트리밍 응답
    - ✅ LCEL 파이프라인
    - ✅ `.invoke()` / `.stream()` 메서드
    """)

    if st.button("🗑️ 대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("AI 에이전트 개발 기술서 - 3장 예제")
