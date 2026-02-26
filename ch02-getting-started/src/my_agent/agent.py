from collections.abc import Iterator

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from my_agent.config import get_settings


def create_model(
    model_name: str | None = None,
) -> BaseChatModel:
    settings = get_settings()
    model_name = model_name or settings.default_model

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

    return init_chat_model(
        model_provider="openai",
        model=model_name,
        api_key=settings.openai_api_key.get_secret_value(),
    )


DEFAULT_SYSTEM_PROMPT = """당신은 친절하고 도움이 되는 AI 어시스턴트입니다.

다음 지침을 따라주세요:
1. 사용자의 질문에 명확하고 간결하게 답변하세요.
2. 확실하지 않은 정보는 추측하지 말고 모른다고 말씀하세요.
3. 필요한 경우 추가 질문을 해서 사용자의 의도를 명확히 파악하세요.
4. 전문 용어를 사용할 때는 쉽게 설명해주세요."""


class Agent:
    def __init__(
        self,
        model: BaseChatModel | None = None,
        system_prompt: str | None = None,
    ):
        self.model = model or create_model()
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.messages: list[BaseMessage] = [SystemMessage(content=self.system_prompt)]

    def chat(self, user_message: str) -> str:
        # 사용자 메시지 추가
        self.messages.append(HumanMessage(content=user_message))

        # LLM 호출
        response = self.model.invoke(self.messages)

        # AI 응답 저장
        self.messages.append(response)

        return response.text

    def stream(self, user_message: str) -> Iterator[str]:
        # 사용자 메시지 추가
        self.messages.append(HumanMessage(content=user_message))

        # 스트리밍 응답 수집
        full_response = ""

        for chunk in self.model.stream(self.messages):
            if chunk.text:
                full_response += chunk.text
                yield chunk.text

        # AI 응답 저장
        self.messages.append(AIMessage(content=full_response))

    def clear_history(self) -> None:
        self.messages = [SystemMessage(content=self.system_prompt)]

    def get_history(self) -> list[dict[str, str]]:
        history = []
        for msg in self.messages[1:]:  # 시스템 메시지 제외
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        return history


def create_agent(
    model_name: str | None = None,
    system_prompt: str | None = None,
) -> Agent:
    model = create_model(model_name=model_name)
    return Agent(model=model, system_prompt=system_prompt)
