"""
4.3-1절 실전 예시: 페르소나와 톤을 적용한 프롬프트.

실행:
    uv run python run_persona.py
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import load_prompt

load_dotenv()


def main() -> None:
    model = init_chat_model(model_provider="openai", model="gpt-5.2")
    prompt = load_prompt("prompts/persona_with_tone.yaml")
    chain = prompt | model

    response = chain.invoke(input={"subject": "API 보안의 주요 위험 요소"})
    print(response.text)


if __name__ == "__main__":
    main()
