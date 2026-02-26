import streamlit as st
from dotenv import load_dotenv

from chatbot import create_chatbot_chain

load_dotenv()

st.set_page_config(
    page_title="Chapter 8: 메모리 챗봇",
    page_icon="💬",
    layout="wide",
)

st.title("💬 Chapter 8: 대화 메모리 챗봇")
st.markdown(
    "LangChain의 `RunnableWithMessageHistory`를 사용한 상태 유지 챗봇입니다."
)

if "chain" not in st.session_state:
    st.session_state.chain = None

if "session_id" not in st.session_state:
    st.session_state.session_id = "default"

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ 설정")

    memory_strategy = st.selectbox(
        "메모리 전략",
        ["Full History", "Window (최근 N개)"],
        help="Full History: 모든 대화 저장, Window: 최근 N개만 유지",
    )

    use_trimming = memory_strategy == "Window (최근 N개)"

    session_id = st.text_input(
        "Session ID (세션)",
        value=st.session_state.session_id,
        help="대화 세션을 구분하는 ID입니다. 다른 ID로 변경하면 새로운 대화가 시작됩니다.",
    )

    if session_id != st.session_state.session_id:
        st.session_state.session_id = session_id
        st.session_state.messages = []
        st.rerun()

    model = st.selectbox(
        "모델",
        ["gpt-5.2"],
        help="사용할 OpenAI 모델을 선택하세요.",
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="응답의 창의성을 조절합니다. 높을수록 더 창의적입니다.",
    )

    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown(
        """
    **메모리 전략 설명**
    - **Full History**: 모든 대화를 저장하여 완전한 맥락 유지
    - **Window**: 최근 N개 메시지만 유지하여 토큰 절약
    """
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        config = {"configurable": {"session_id": st.session_state.session_id}}

        try:
            chain = create_chatbot_chain(
                use_trimming=use_trimming, model_name=model, temperature=temperature
            )

            response = chain.invoke({"input": prompt}, config=config)

            full_response = response.text
            message_placeholder.markdown(full_response)

        except Exception as e:
            error_msg = f"❌ 오류가 발생했습니다: {str(e)}"
            message_placeholder.error(error_msg)
            full_response = error_msg

    st.session_state.messages.append({"role": "assistant", "content": full_response})
