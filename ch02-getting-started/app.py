"""
Streamlit 채팅 애플리케이션

AI 에이전트와 대화할 수 있는 웹 인터페이스를 제공합니다.

실행 방법:
    uv run streamlit run app.py
"""

import streamlit as st

from my_agent import create_agent, get_settings

# 페이지 설정
st.set_page_config(
    page_title="My AI Agent",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")

    # 모델 선택
    model_options = ["gpt-5.2"]
    model_name = st.selectbox(
        "모델",
        options=model_options,
        index=0,
        help="사용할 모델을 선택하세요",
    )

    # 커스텀 시스템 프롬프트
    custom_prompt = st.text_area(
        "시스템 프롬프트 (선택)",
        value="",
        height=100,
        help="커스텀 시스템 프롬프트를 입력하세요. 비워두면 기본값을 사용합니다.",
    )

    st.divider()

    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        if "agent" in st.session_state:
            st.session_state.agent.clear_history()
        st.rerun()

    # 설정 정보 표시
    st.divider()
    st.caption("📌 현재 설정")
    settings = get_settings()
    st.caption(f"- 디버그 모드: {'켜짐' if settings.debug else '꺼짐'}")

# 메인 화면
st.title("🤖 My AI Agent")
st.caption("LangChain으로 만든 AI 에이전트와 대화해보세요!")

# 에이전트 초기화 또는 재생성
agent_key = f"openai_{model_name}_{hash(custom_prompt)}"

if "agent_key" not in st.session_state or st.session_state.agent_key != agent_key:
    try:
        with st.spinner("에이전트 초기화 중..."):
            st.session_state.agent = create_agent(
                model_name=model_name,
                system_prompt=custom_prompt if custom_prompt else None,
            )
            st.session_state.agent_key = agent_key
            st.session_state.messages = []
    except ValueError as e:
        st.error(f"❌ 에이전트 초기화 실패: {e}")
        st.info("💡 .env 파일에 API 키가 설정되어 있는지 확인하세요.")
        st.stop()
    except Exception as e:
        st.error(f"❌ 에이전트 초기화 실패: {e}")
        st.stop()

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성 (스트리밍)
    with st.chat_message("assistant"):
        try:
            response = st.write_stream(st.session_state.agent.stream(prompt))
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_msg = f"응답 생성 중 오류가 발생했습니다: {e}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
