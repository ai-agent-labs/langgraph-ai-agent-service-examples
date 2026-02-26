import os
from collections.abc import Iterator

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)

from qa_chatbot.config import get_settings
from qa_chatbot.prompts import DEFAULT_QA_PROMPT


def create_model(
    model_name: str | None = None,
    temperature: float | None = None,
) -> BaseChatModel:
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
    prompt = prompt or DEFAULT_QA_PROMPT
    model = model or create_model()
    return prompt | model | StrOutputParser()


def create_qa_chain_with_postprocessing(
    prompt: ChatPromptTemplate | None = None,
    model: BaseChatModel | None = None,
) -> Runnable:
    prompt = prompt or DEFAULT_QA_PROMPT
    model = model or create_model()

    def add_ai_indicator(message: AIMessage) -> AIMessage:
        message.content += "\n\n(이 응답은 AI에 의해 생성되었습니다.)"
        return message

    return prompt | model | RunnableLambda(add_ai_indicator) | StrOutputParser()


def create_parallel_chain(model: BaseChatModel | None = None) -> Runnable:
    model = model or create_model()

    # 1. 긍정적 설명 체인
    prompt_pros = PromptTemplate.from_template(
        "{subject}에 대해 긍정적인 설명을 해 주세요"
    )
    pros_chain = prompt_pros | model | StrOutputParser()

    # 2. 비판적 설명 체인
    prompt_cons = PromptTemplate.from_template(
        "{subject}에 대해 비판적인 설명을 해 주세요"
    )
    cons_chain = prompt_cons | model | StrOutputParser()

    # 3. 종합 프롬프트
    prompt_aggregate = PromptTemplate.from_template(
        """다음 두 설명을 종합해서 {subject}에 대한 균형잡힌 시각을 제시해 주세요.

긍정적인 설명: {pros}

비판적인 설명: {cons}"""
    )

    # 4. 병렬 실행 후 종합
    return (
        RunnableParallel(
            pros=pros_chain, cons=cons_chain, subject=RunnablePassthrough()
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
