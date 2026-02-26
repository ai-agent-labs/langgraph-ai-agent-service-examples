from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

DEFAULT_QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """당신은 친절하고 도움이 되는 Q&A 어시스턴트입니다.

사용자의 질문에 명확하고 간결하게 답변하세요.""",
        ),
        ("user", "{question}"),
    ]
)

CONVERSATIONAL_QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 친절하고 도움이 되는 Q&A 어시스턴트입니다."),
        MessagesPlaceholder("history"),
        ("user", "{question}"),
    ]
)

EXPERT_QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 {domain} 분야의 전문가입니다."),
        ("user", "{question}"),
    ]
)
