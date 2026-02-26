import sys
from pathlib import Path

examples_dir = Path(__file__).parent
sys.path.insert(0, str(examples_dir))
sys.path.insert(0, str(examples_dir / "shared"))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from shared.navigation import render_sidebar, get_chapter_info
from shared.styles import apply_common_styles, render_chapter_header
from shared.utils import render_env_warning

st.set_page_config(
    page_title="AI 에이전트 실습",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_common_styles()


def render_home():
    st.title("🤖 AI 에이전트 개발 실습")
    st.markdown(
        """
        **LangChain & LangGraph 기술서** 예제 프로젝트에 오신 것을 환영합니다!

        왼쪽 사이드바에서 챕터를 선택하여 실습을 시작하세요.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 📚 기초
            - **Ch03**: LCEL 파이프라인
            - **Ch06**: 대화 메모리
            - **Ch08**: 구조화된 출력
            """
        )

    with col2:
        st.markdown(
            """
            ### 🔧 도구와 워크플로우
            - **Ch07**: 도구 호출
            - **Ch09**: LangGraph 라우팅
            """
        )

    with col3:
        st.markdown(
            """
            ### 🤖 에이전트와 고급
            - **Ch10**: ReAct 패턴
            - **Ch11**: Supervisor 패턴
            - **Ch05**: RAG 검색
            - **Ch13**: 평가 & 모니터링
            """
        )

    st.divider()

    # 학습 흐름 안내
    st.subheader("📈 권장 학습 순서")
    st.markdown(
        """
        ```
        Ch03 (기본 체인) → Ch06 (메모리) → Ch07 (도구) → Ch08 (구조화)
                                    ↓
                            Ch09 (LangGraph)
                                    ↓
                            Ch10 (단일 에이전트)
                                    ↓
                            Ch11 (멀티에이전트)
                                    ↓
                        Ch05 (RAG) → Ch13 (평가)
        ```
        """
    )

    # 환경 설정 상태
    st.subheader("⚙️ 환경 설정")
    render_env_warning()


def load_chapter_page(chapter_id: str):
    chapter_info = get_chapter_info(chapter_id)
    if not chapter_info:
        st.error(f"챕터 {chapter_id}를 찾을 수 없습니다.")
        return

    render_chapter_header(
        chapter_id=chapter_id,
        title=chapter_info["name"],
        description=chapter_info["desc"],
    )

    if not render_env_warning():
        return

    try:
        chapter_dir = chapter_info.get("dir")
        if not chapter_dir:
            st.error(f"챕터 디렉토리를 찾을 수 없습니다: {chapter_id}")
            return

        chapter_path = examples_dir / chapter_dir
        src_path = chapter_path / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))

        # page.py 로드
        page_path = chapter_path / "page.py"
        if page_path.exists():
            import importlib.util

            spec = importlib.util.spec_from_file_location(f"{chapter_id}_page", page_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "render"):
                module.render()
            else:
                st.warning("render() 함수가 page.py에 정의되지 않았습니다.")
        else:
            # page.py가 없으면 기존 app.py 안내
            st.info(
                f"""
                이 챕터는 독립 실행 모드를 사용합니다.

                ```bash
                cd {chapter_dir}
                uv run streamlit run app.py
                ```
                """
            )

    except Exception as e:
        st.error(f"챕터 로드 중 오류: {e}")
        import traceback

        st.code(traceback.format_exc())


def main():
    current_chapter = render_sidebar()

    if current_chapter:
        load_chapter_page(current_chapter)
    else:
        render_home()


if __name__ == "__main__":
    main()
