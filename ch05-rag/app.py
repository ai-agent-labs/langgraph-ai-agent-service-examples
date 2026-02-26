"""
Streamlit RAG 채팅 애플리케이션

RAG 기반 AI 에이전트와 대화할 수 있는 웹 인터페이스를 제공합니다.

실행 방법:
    # OpenSearch 시작 (처음 한 번)
    docker compose up -d

    # 앱 실행
    uv run streamlit run app.py
"""

import streamlit as st

from rag_agent import (
    create_agentic_rag_agent,
    create_rag_agent,
    get_settings,
    setup_sample_index,
)
from rag_agent.indexer import create_opensearch_client

# 페이지 설정
st.set_page_config(
    page_title="RAG Agent",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)


def check_opensearch_connection() -> bool:
    """OpenSearch 연결 상태를 확인합니다."""
    try:
        client = create_opensearch_client()
        client.info()
        return True
    except Exception:
        return False


def check_index_exists() -> bool:
    """인덱스 존재 여부를 확인합니다."""
    try:
        settings = get_settings()
        client = create_opensearch_client()
        return client.indices.exists(index=settings.index_name)
    except Exception:
        return False


# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")

    # RAG 모드 선택
    rag_mode = st.selectbox(
        "RAG 모드",
        options=["기본 RAG", "에이전틱 RAG"],
        index=0,
        help="기본 RAG: 단일 검색 후 답변\n에이전틱 RAG: 필요에 따라 여러 번 검색",
    )

    # 기본 RAG 옵션
    if rag_mode == "기본 RAG":
        search_type = st.selectbox(
            "검색 방식",
            options=["hybrid", "vector"],
            format_func=lambda x: "하이브리드" if x == "hybrid" else "벡터",
            index=0,
            help="하이브리드: 벡터 + 키워드 검색 결합",
        )
        use_rerank = st.checkbox(
            "리랭킹 사용",
            value=True,
            help="Cross-Encoder로 검색 결과 재정렬",
        )
    else:
        search_type = "hybrid"
        use_rerank = True

    st.divider()

    # OpenSearch 상태
    st.caption("📊 시스템 상태")

    opensearch_ok = check_opensearch_connection()
    if opensearch_ok:
        st.success("OpenSearch 연결됨", icon="✅")

        # 인덱스 상태
        if check_index_exists():
            st.success("인덱스 준비됨", icon="✅")
        else:
            st.warning("인덱스 없음", icon="⚠️")
            if st.button("📥 샘플 데이터 인덱싱", use_container_width=True):
                with st.spinner("인덱싱 중..."):
                    try:
                        count = setup_sample_index()
                        st.success(f"{count}개 청크 인덱싱 완료!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"인덱싱 실패: {e}")
    else:
        st.error("OpenSearch 연결 실패", icon="❌")
        st.info("docker compose up -d 로 OpenSearch를 시작하세요")

    st.divider()

    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        if "agent" in st.session_state:
            st.session_state.agent.clear_history()
        st.rerun()

# 메인 화면
st.title("📚 RAG Agent")
st.caption("회사 정책 문서를 기반으로 질문에 답변합니다")

# OpenSearch 연결 확인
if not opensearch_ok:
    st.error("OpenSearch가 실행되지 않았습니다.")
    st.code("docker compose up -d", language="bash")
    st.stop()

# 인덱스 확인
if not check_index_exists():
    st.warning("먼저 사이드바에서 '샘플 데이터 인덱싱'을 실행하세요.")
    st.stop()

# 에이전트 초기화
agent_key = f"{rag_mode}_{search_type}_{use_rerank}"

if "agent_key" not in st.session_state or st.session_state.agent_key != agent_key:
    try:
        with st.spinner("에이전트 초기화 중..."):
            if rag_mode == "에이전틱 RAG":
                st.session_state.agent = create_agentic_rag_agent()
            else:
                st.session_state.agent = create_rag_agent(
                    search_type=search_type,
                    use_rerank=use_rerank,
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
if prompt := st.chat_input("질문을 입력하세요... (예: 연차휴가는 며칠인가요?)"):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        try:
            # 에이전틱 RAG는 스트리밍 미지원
            if rag_mode == "에이전틱 RAG":
                with st.spinner("검색 및 분석 중..."):
                    response = st.session_state.agent.chat(prompt)
                st.markdown(response)
            else:
                # 기본 RAG는 스트리밍 지원
                response = st.write_stream(st.session_state.agent.stream(prompt))

            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
        except Exception as e:
            error_msg = f"응답 생성 중 오류가 발생했습니다: {e}"
            st.error(error_msg)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )

# 하단 정보
st.divider()
st.caption("💡 예시 질문: 연차휴가 신청 방법, 재택근무 가능 일수, 출장 정산 방법")
