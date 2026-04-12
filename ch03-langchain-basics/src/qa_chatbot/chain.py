import os
from collections.abc import Iterator

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import (
    Runnable,
    RunnableParallel,
    RunnablePassthrough,
)

from qa_chatbot.config import get_settings
from qa_chatbot.prompts import DEFAULT_QA_PROMPT


def create_model(
    model_name: str | None = None,
    temperature: float | None = None,
) -> BaseChatModel:
    """LLM 모델을 생성합니다."""
    settings = get_settings()
    model_name = model_name or settings.default_model
    temperature = temperature if temperature is not None else settings.temperature

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

    os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()

    return init_chat_model(
        model_name,
        model_provider="openai",
        temperature=temperature,
        max_tokens=settings.max_tokens,
    )


def create_qa_chain(
    prompt: ChatPromptTemplate | None = None,
    model: BaseChatModel | None = None,
) -> Runnable:
    """`prompt | model | StrOutputParser()` 형태의 기본 QA 체인을 구성합니다."""
    prompt = prompt or DEFAULT_QA_PROMPT
    model = model or create_model()
    return prompt | model | StrOutputParser()


def create_controversial_chain(model: BaseChatModel | None = None) -> Runnable:
    """한 주제에 대해 긍정적 설명과 비판적 설명을 병렬로 생성한 뒤,
    종합 프롬프트로 균형 잡힌 시각을 돌려주는 체인입니다.
    """
    model = model or create_model()

    # A. 긍정적인 Prompt를 통해 설명 생성
    prompt_pros = PromptTemplate.from_template(
        "{subject}에 대해 긍정적인 설명을 해 주세요.",
    )
    pros_chain = prompt_pros | model

    # B. 비판적인 Prompt를 통해 설명 생성
    prompt_cons = PromptTemplate.from_template(
        "{subject}에 대해 비판적인 설명을 해 주세요.",
    )
    cons_chain = prompt_cons | model

    # C. 두 설명을 종합하는 프롬프트
    prompt_aggregate = PromptTemplate.from_template(
        "다음 두 설명을 종합해서 {subject}에 대한 균형 잡힌 시각을 제시해 주세요.\n\n"
        "긍정적인 설명: {pros}\n\n"
        "비판적인 설명: {cons}"
    )

    return (
        RunnableParallel(
            {
                "pros": pros_chain,
                "cons": cons_chain,
                "subject": RunnablePassthrough(),
            }
        )
        | prompt_aggregate
        | model
        | StrOutputParser()
    )


def run_qa(question: str, chain: Runnable | None = None) -> str:
    if chain is None:
        chain = create_qa_chain()
    return chain.invoke({"question": question})


def stream_qa(question: str, chain: Runnable | None = None) -> Iterator[str]:
    if chain is None:
        chain = create_qa_chain()

    for chunk in chain.stream({"question": question}):
        yield chunk
