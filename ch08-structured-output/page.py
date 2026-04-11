import streamlit as st

from info_extractor import extract_leave_request


def render():
    # 사이드바 정보
    with st.sidebar:
        st.subheader("📋 구조화된 출력")
        st.markdown("""
        ```python
        model.with_structured_output(LeaveRequest)
        ```

        **주요 기능:**
        - Pydantic 스키마 → JSON
        - 타입 안전성 보장
        - 자동 검증
        """)

    st.subheader("휴가 신청 정보 추출")
    leave_text = st.text_area(
        "요청 텍스트",
        value="EMP001 직원이 12월 23일부터 25일까지 경조사 휴가 신청합니다. 부친상으로 인해 급히 신청합니다.",
        height=120,
        key="ch08_leave_text",
    )

    if st.button("추출", key="ch08_leave_btn"):
        with st.spinner("추출 중..."):
            try:
                result = extract_leave_request(leave_text)
                st.success("추출 완료!")
                st.json(result.model_dump())
            except Exception as e:
                st.error(f"오류: {str(e)}")
