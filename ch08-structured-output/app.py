"""구조화된 출력 Streamlit 애플리케이션"""

import streamlit as st
from dotenv import load_dotenv

from info_extractor import extract_contact_info, extract_movie_info

load_dotenv()

st.set_page_config(
    page_title="정보 추출기",
    page_icon="📋",
    layout="centered",
)

st.title("📋 정보 추출기")
st.caption("🚀 LangChain 구조화된 출력 예제")

tab1, tab2 = st.tabs(["연락처 추출", "영화 정보 추출"])

with tab1:
    st.subheader("연락처 정보 추출")
    contact_text = st.text_area(
        "텍스트 입력",
        value="김철수입니다. 이메일은 kim@example.com이고 전화번호는 010-1234-5678입니다.",
        height=100,
    )

    if st.button("추출", key="contact"):
        with st.spinner("추출 중..."):
            try:
                result = extract_contact_info(contact_text)
                st.success("추출 완료!")
                st.json(result.model_dump())
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")

with tab2:
    st.subheader("영화 정보 추출")
    movie_text = st.text_area(
        "텍스트 입력",
        value="인셉션은 2010년에 개봉한 크리스토퍼 놀란 감독의 작품입니다. 평점은 8.8점입니다.",
        height=100,
    )

    if st.button("추출", key="movie"):
        with st.spinner("추출 중..."):
            try:
                result = extract_movie_info(movie_text)
                st.success("추출 완료!")
                st.json(result.model_dump())
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")

with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    ### with_structured_output

    ```python
    model = init_chat_model("gpt-5.2")
    structured_llm = model.with_structured_output(Schema)
    result = structured_llm.invoke("...")
    ```

    **주요 기능:**
    - ✅ Pydantic 스키마 → JSON 출력
    - ✅ 타입 안전성 보장
    - ✅ 자동 검증
    """)
    st.divider()
    st.caption("AI 에이전트 개발 기술서 - 8장 예제")
