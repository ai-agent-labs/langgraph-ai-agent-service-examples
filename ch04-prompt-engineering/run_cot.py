"""
4.3-3절 실전 예시: 사고 연쇄(Chain of Thought) 프롬프팅.

실행:
    uv run python run_cot.py
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import load_prompt

load_dotenv()


def main() -> None:
    model = init_chat_model(model_provider="openai", model="gpt-5.2")
    prompt = load_prompt("prompts/with_cot.yaml")
    chain = prompt | model

    question = (
        "한 반에 학생이 30명 있습니다. 그중 60%가 남학생이고, "
        "남학생 중 절반이 안경을 씁니다. 안경을 쓴 남학생은 몇 명인가요?"
    )
    response = chain.invoke(input={"question": question})
    print(response.text)


if __name__ == "__main__":
    main()
