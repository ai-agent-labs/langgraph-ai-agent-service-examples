from langchain.chat_models import init_chat_model
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory

from chatbot.config import get_settings

chat_histories = {}


def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in chat_histories:
        chat_histories[session_id] = InMemoryChatMessageHistory()
    return chat_histories[session_id]


def create_chatbot_chain(
    use_trimming: bool = False,
    model_name: str | None = None,
    temperature: float | None = None,
) -> Runnable:
    settings = get_settings()
    model_name = model_name or settings.default_model
    temperature = temperature if temperature is not None else settings.temperature
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "당신은 친절한 HR 상담 어시스턴트입니다. 직원의 휴가, 급여, 복리후생 관련 질문에 답변합니다."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    model = init_chat_model(
        model_provider="openai", model=model_name, temperature=temperature
    )

    if use_trimming:
        # Window 메모리 전략: 최근 N개 메시지만 유지
        trimmer = trim_messages(
            max_tokens=1000,
            strategy="last",
            token_counter=len,
            include_system=True,
            start_on="human",
        )

        chain = (
            {
                "history": lambda x: trimmer.invoke(x["history"]),
                "input": lambda x: x["input"],
            }
            | prompt
            | model
        )
    else:
        # Full History 전략: 모든 대화 기록 유지
        chain = prompt | model

    return RunnableWithMessageHistory(
        chain,
        get_chat_history,
        input_messages_key="input",
        history_messages_key="history",
    )
