import streamlit as st


def apply_common_styles():
    st.markdown(
        """
        <style>
        /* 사이드바 버튼 스타일 */
        .stButton > button {
            text-align: left;
            padding: 0.5rem 1rem;
        }

        /* 챕터 헤더 스타일 */
        .chapter-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 1rem;
        }

        /* 채팅 메시지 스타일 */
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
        }

        .user-message {
            background-color: #e3f2fd;
        }

        .assistant-message {
            background-color: #f5f5f5;
        }

        /* 도구 호출 표시 */
        .tool-call {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 0.5rem 1rem;
            margin: 0.5rem 0;
            font-family: monospace;
            font-size: 0.85rem;
        }

        /* 정보 카드 */
        .info-card {
            background-color: #e8f5e9;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_chapter_header(chapter_id: str, title: str, description: str):
    st.markdown(
        f"""
        <div class="chapter-header">
            <h2>{chapter_id.upper()}: {title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
