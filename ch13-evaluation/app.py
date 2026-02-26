"""
Streamlit RAG + Langfuse 평가 애플리케이션

Langfuse 관찰성이 연동된 RAG 기반 AI 에이전트와
대화할 수 있는 웹 인터페이스를 제공합니다.

실행 방법:
    uv run streamlit run app.py
"""

import streamlit as st

from eval_agent import (
    RAGAgent,
    create_rag_agent,
    create_score,
    evaluate_response,
    flush_langfuse,
    get_langfuse_client,
    get_settings,
    init_langfuse,
    setup_sample_vectorstore,
)

# 페이지 설정
st.set_page_config(
    page_title="RAG + Langfuse Demo",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded",
)


def init_app() -> bool:
    """앱을 초기화합니다."""
    try:
        # 설정 로드 확인
        settings = get_settings()

        # Langfuse 초기화
        init_langfuse()

        # 벡터 저장소 설정
        if "vectorstore_ready" not in st.session_state:
            setup_sample_vectorstore()
            st.session_state.vectorstore_ready = True

        return True
    except Exception as e:
        st.error(f"초기화 실패: {e}")
        return False


# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")

    # Langfuse 설정 표시
    st.caption("📊 Langfuse 연동")

    try:
        settings = get_settings()
        st.success("Langfuse 연결됨", icon="✅")
        st.caption(f"Host: {settings.langfuse_host}")
        st.caption(f"샘플링: {settings.langfuse_sample_rate * 100:.0f}%")
        st.caption(f"마스킹: {'켜짐' if settings.langfuse_enable_masking else '꺼짐'}")
    except Exception:
        st.error("설정 로드 실패", icon="❌")
        st.info("`.env` 파일을 확인하세요")

    st.divider()

    # 평가 옵션
    st.caption("🎯 자동 평가")
    auto_evaluate = st.checkbox(
        "응답 자동 평가",
        value=True,
        help="매 응답마다 Faithfulness와 Relevance를 평가합니다",
    )

    st.divider()

    # 피드백 섹션
    st.caption("👍 사용자 피드백")
    if "last_trace_id" in st.session_state and st.session_state.last_trace_id:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 좋아요", use_container_width=True):
                create_score(
                    trace_id=st.session_state.last_trace_id,
                    name="user-feedback",
                    value=1,
                    comment="사용자 좋아요",
                )
                flush_langfuse()
                st.success("피드백 저장됨!")
        with col2:
            if st.button("👎 별로예요", use_container_width=True):
                create_score(
                    trace_id=st.session_state.last_trace_id,
                    name="user-feedback",
                    value=0,
                    comment="사용자 싫어요",
                )
                flush_langfuse()
                st.success("피드백 저장됨!")
    else:
        st.caption("대화 후 피드백을 남길 수 있습니다")

    st.divider()

    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_trace_id = None
        if "agent" in st.session_state:
            st.session_state.agent.clear_history()
        st.rerun()

# 메인 화면
st.title("📊 RAG + Langfuse Demo")
st.caption("Langfuse로 관찰성이 연동된 RAG 채팅 애플리케이션")

# 초기화
if not init_app():
    st.error("앱 초기화에 실패했습니다.")
    st.info("💡 `.env` 파일에 필요한 API 키가 설정되어 있는지 확인하세요.")
    st.code(
        """
# .env 파일 예시
OPENAI_API_KEY=sk-proj-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
    """,
        language="bash",
    )
    st.stop()

# 에이전트 초기화
if "agent" not in st.session_state:
    try:
        st.session_state.agent = create_rag_agent()
        st.session_state.messages = []
        st.session_state.last_trace_id = None
    except Exception as e:
        st.error(f"에이전트 초기화 실패: {e}")
        st.stop()

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_trace_id" not in st.session_state:
    st.session_state.last_trace_id = None

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # 평가 결과 표시
        if "evaluation" in message:
            eval_result = message["evaluation"]
            with st.expander("📊 평가 결과"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Faithfulness", f"{eval_result['faithfulness']:.2f}")
                col2.metric("Relevance", f"{eval_result['relevance']:.2f}")
                col3.metric("Overall", f"{eval_result['overall']:.2f}")

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요... (예: 연차휴가는 며칠인가요?)"):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        try:
            # 스트리밍 응답
            response = st.write_stream(st.session_state.agent.stream(prompt))

            message_data = {"role": "assistant", "content": response}

            # 자동 평가
            if auto_evaluate:
                with st.spinner("응답 평가 중..."):
                    # 마지막 대화의 컨텍스트 가져오기
                    from eval_agent.rag_chain import retrieve_documents

                    docs = retrieve_documents(prompt)
                    context = "\n".join([doc.page_content for doc in docs])

                    eval_result = evaluate_response(
                        question=prompt,
                        answer=response,
                        context=context,
                    )

                    message_data["evaluation"] = eval_result

                    # 평가 결과 표시
                    with st.expander("📊 평가 결과"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Faithfulness", f"{eval_result['faithfulness']:.2f}")
                        col2.metric("Relevance", f"{eval_result['relevance']:.2f}")
                        col3.metric("Overall", f"{eval_result['overall']:.2f}")

            st.session_state.messages.append(message_data)

            # Langfuse 플러시
            flush_langfuse()

        except Exception as e:
            error_msg = f"응답 생성 중 오류가 발생했습니다: {e}"
            st.error(error_msg)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )

# 하단 정보
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("💡 예시 질문: 연차휴가, 재택근무, 출장비 정산")
with col2:
    st.caption("📊 [Langfuse 대시보드](https://cloud.langfuse.com)에서 트레이스 확인")
