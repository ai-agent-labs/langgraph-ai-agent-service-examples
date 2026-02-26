import streamlit as st


def render():
    st.info(
        """
        ### 📊 평가 예제는 독립 실행을 권장합니다

        Ch13은 Langfuse 연동이 필요하여 별도 설정이 필요합니다.
        """
    )

    st.subheader("🚀 실행 방법")

    st.code(
        """
# 1. 환경 변수 설정 (.env)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com

# 2. 앱 실행
cd ch13-evaluation
uv run streamlit run app.py
        """,
        language="bash",
    )

    st.subheader("📋 주요 기능")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **관찰성:**
        - Langfuse 트레이싱
        - 토큰 사용량 추적
        - 지연시간 모니터링
        """)

    with col2:
        st.markdown("""
        **자동 평가:**
        - Faithfulness (사실성)
        - Relevance (관련성)
        - 사용자 피드백 수집
        """)

    st.divider()
    st.caption("💡 Langfuse 대시보드에서 상세 분석 가능")
