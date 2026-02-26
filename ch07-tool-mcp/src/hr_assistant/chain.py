from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from hr_assistant.config import get_settings
from hr_assistant.tools import HR_TOOLS

HR_SYSTEM_PROMPT = """당신은 HR 정책 어시스턴트입니다.
직원들의 연차 조회, 정책 검색, 휴가 신청을 도와드립니다.

사용 가능한 도구:
- check_leave_balance: 직원의 연차 잔여일수 조회
- search_policy: HR 정책 키워드 검색
- submit_leave_request: 휴가 신청 제출

도구를 사용하여 정확한 정보를 제공하세요."""


def create_hr_agent() -> BaseChatModel:
    settings = get_settings()
    model = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=settings.temperature,
    )
    return model.bind_tools(HR_TOOLS)


def execute_tools(ai_message: AIMessage) -> list[ToolMessage]:
    tool_results = []
    tools_dict = {tool.name: tool for tool in HR_TOOLS}

    for tool_call in ai_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        if tool_name in tools_dict:
            result = tools_dict[tool_name].invoke(tool_args)
            tool_results.append(ToolMessage(content=str(result), tool_call_id=tool_id))

    return tool_results


def chat_with_tools(user_message: str) -> str:
    agent = create_hr_agent()
    messages = [
        {"role": "system", "content": HR_SYSTEM_PROMPT},
        HumanMessage(content=user_message),
    ]

    ai_message = agent.invoke(messages)

    if not ai_message.tool_calls:
        return ai_message.text

    tool_results = execute_tools(ai_message)
    messages.extend([ai_message, *tool_results])

    final_message = agent.invoke(messages)
    return final_message.text
