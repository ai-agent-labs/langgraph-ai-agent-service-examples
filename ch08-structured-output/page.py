import streamlit as st
from info_extractor import extract_contact_info, extract_movie_info


def render():
    # 사이드바 정보
    with st.sidebar:
        st.subheader("📋 구조화된 출력")
        st.markdown("""
        ```python
        model.with_structured_output(Schema)
        ```

        **주요 기능:**
        - Pydantic 스키마 → JSON
        - 타입 안전성 보장
        - 자동 검증
        """)

    # 탭 구성
    tab1, tab2 = st.tabs(["📇 연락처 추출", "🎬 영화 정보 추출"])

    with tab1:
        st.subheader("연락처 정보 추출")
        contact_text = st.text_area(
            "텍스트 입력",
            value="김철수입니다. 이메일은 kim@example.com이고 전화번호는 010-1234-5678입니다.",
            height=100,
            key="ch08_contact_text",
        )

        if st.button("추출", key="ch08_contact_btn"):
            with st.spinner("추출 중..."):
                try:
                    result = extract_contact_info(contact_text)
                    st.success("추출 완료!")
                    st.json(result.model_dump())
                except Exception as e:
                    st.error(f"오류: {str(e)}")

    with tab2:
        st.subheader("영화 정보 추출")
        movie_text = st.text_area(
            "텍스트 입력",
            value="인셉션은 2010년에 개봉한 크리스토퍼 놀란 감독의 작품입니다. 평점은 8.8점입니다.",
            height=100,
            key="ch08_movie_text",
        )

        if st.button("추출", key="ch08_movie_btn"):
            with st.spinner("추출 중..."):
                try:
                    result = extract_movie_info(movie_text)
                    st.success("추출 완료!")
                    st.json(result.model_dump())
                except Exception as e:
                    st.error(f"오류: {str(e)}")
