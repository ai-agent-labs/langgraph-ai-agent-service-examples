import streamlit as st


def render():
    st.info(
        """
        ### 📚 RAG 예제는 독립 실행을 권장합니다

        Ch07 RAG는 OpenSearch 연동이 필요하여 별도 환경 구성이 필요합니다.
        """
    )

    st.subheader("🚀 실행 방법")

    st.code(
        """
# 1. OpenSearch 시작
cd ch05-rag
docker compose up -d

# 2. 앱 실행
uv run streamlit run app.py
        """,
        language="bash",
    )

    st.subheader("📋 주요 기능")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **검색 방식:**
        - 벡터 검색 (임베딩)
        - 하이브리드 검색 (벡터 + 키워드)
        - Cross-Encoder 리랭킹
        """)

    with col2:
        st.markdown("""
        **RAG 모드:**
        - 기본 RAG: 단일 검색 → 응답
        - 에이전틱 RAG: 다중 검색 루프
        """)

    st.divider()
    st.caption("💡 HR 정책 문서 기반 질의응답 시스템")
