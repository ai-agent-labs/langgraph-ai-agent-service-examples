"""구조화된 출력 Streamlit 애플리케이션 (책 8장 LeaveRequest 예제)"""

import streamlit as st
from dotenv import load_dotenv

from info_extractor import extract_leave_request

load_dotenv()

st.set_page_config(
    page_title="휴가 신청 추출기",
    page_icon="📋",
    layout="centered",
)

st.title("📋 휴가 신청 정보 추출기")
st.caption("🚀 LangChain 구조화된 출력 예제 — LeaveRequest 스키마")

st.subheader("자유 형식 요청에서 휴가 신청 정보 추출")
leave_text = st.text_area(
    "요청 텍스트",
    value="EMP001 직원이 12월 23일부터 25일까지 경조사 휴가 신청합니다. 부친상으로 인해 급히 신청합니다.",
    height=120,
)

if st.button("추출", key="leave"):
    with st.spinner("추출 중..."):
        try:
            result = extract_leave_request(leave_text)
            st.success("추출 완료!")
            st.json(result.model_dump())
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")

with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    ### with_structured_output

    ```python
    from pydantic import BaseModel, Field
    from langchain.chat_models import init_chat_model

    class LeaveRequest(BaseModel):
        employee_id: str
        leave_type: str
        start_date: str
        end_date: str
        reason: str

    model = init_chat_model("gpt-5.2")
    structured_llm = model.with_structured_output(LeaveRequest)
    result = structured_llm.invoke("...")
    ```

    **주요 기능:**
    - ✅ Pydantic 스키마 → JSON 출력
    - ✅ 타입 안전성 보장
    - ✅ 자동 검증
    """)
    st.divider()
    st.caption("AI 에이전트 개발 기술서 - 8장 예제")
