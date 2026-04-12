"""
4.2-3절 실전 예시: 구조화 프롬프트로 이메일 요약하기.

실행:
    uv run python run_email_summary.py
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import load_prompt

load_dotenv()


def main() -> None:
    model = init_chat_model(model_provider="openai", model="gpt-5.2")
    prompt = load_prompt("prompts/email_summary.yaml")
    chain = prompt | model

    email = """안녕하세요, 개발팀 여러분

다음 주 금요일 오후 2시에 Q4 스프린트 회고 및 2026년 로드맵 논의를 위한 전체 회의를 진행하고자 합니다.
회의실은 본사 3층 대회의실이며, 원격 참여자를 위해 Zoom 링크도 별도로 공유드리겠습니다.
주요 안건은 다음과 같습니다.
1. Q4 스프린트 성과 및 KPI 달성 현황 검토
2. 고객 피드백 기반 개선사항 논의
3. 2026년 상반기 주요 기능 로드맵 수립
4. 신규 프로젝트팀 구성 및 역할 분담
각자 담당하신 프로젝트의 진행 현황과 이슈사항을 정리해 와 주시기 바랍니다.
참석이 어려우신 분은 수요일까지 말씀 부탁드립니다.
감사합니다."""

    response = chain.invoke(input={"email": email})
    print(response.text)


if __name__ == "__main__":
    main()
