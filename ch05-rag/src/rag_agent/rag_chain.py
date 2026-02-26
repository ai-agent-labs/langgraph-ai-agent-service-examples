from collections.abc import Iterator

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from rag_agent.config import get_settings
from rag_agent.reranker import search_with_rerank
from rag_agent.search import format_search_results, hybrid_search, vector_search


def create_llm(model_name: str | None = None) -> BaseChatModel:
    settings = get_settings()
    model_name = model_name or settings.default_model
    return init_chat_model(
        model_provider="openai",
        model=model_name,
        temperature=0,
        api_key=settings.openai_api_key.get_secret_value(),
    )


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """당신은 회사 정책 안내 도우미입니다.
주어진 문서만을 참고하여 질문에 답변하세요.

규칙:
1. 문서에 있는 내용만 답변하세요
2. 문서에 없는 내용은 "해당 정보는 문서에서 확인할 수 없습니다"라고 답변하세요
3. 답변 끝에 참고한 문서 출처를 명시하세요
4. 친절하고 명확하게 답변하세요""",
        ),
        (
            "user",
            """[참고 문서]
{context}

[질문]
{question}""",
        ),
    ]
)


def ask_rag(
    question: str,
    search_type: str = "hybrid",
    use_rerank: bool = True,
) -> str:
    # 1. 검색
    if use_rerank:
        results = search_with_rerank(question)
    elif search_type == "vector":
        results = vector_search(question)
    else:
        results = hybrid_search(question)

    # 2. 컨텍스트 구성
    context = format_search_results(results, include_score=False)

    # 3. LLM 답변 생성
    llm = create_llm()
    chain = RAG_PROMPT | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})


def stream_rag(
    question: str,
    search_type: str = "hybrid",
    use_rerank: bool = True,
) -> Iterator[str]:
    if use_rerank:
        results = search_with_rerank(question)
    elif search_type == "vector":
        results = vector_search(question)
    else:
        results = hybrid_search(question)

    context = format_search_results(results, include_score=False)
    llm = create_llm()
    chain = RAG_PROMPT | llm | StrOutputParser()
    yield from chain.stream({"context": context, "question": question})


class RAGAgent:
    def __init__(
        self,
        search_type: str = "hybrid",
        use_rerank: bool = True,
    ):
        self.search_type = search_type
        self.use_rerank = use_rerank
        self.history: list[dict[str, str]] = []

    def chat(self, question: str) -> str:
        answer = ask_rag(
            question,
            search_type=self.search_type,
            use_rerank=self.use_rerank,
        )
        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": answer})
        return answer

    def stream(self, question: str) -> Iterator[str]:
        self.history.append({"role": "user", "content": question})
        full_response = ""
        for chunk in stream_rag(
            question,
            search_type=self.search_type,
            use_rerank=self.use_rerank,
        ):
            full_response += chunk
            yield chunk
        self.history.append({"role": "assistant", "content": full_response})

    def clear_history(self) -> None:
        self.history = []

    def get_history(self) -> list[dict[str, str]]:
        return self.history


def create_rag_agent(
    search_type: str = "hybrid",
    use_rerank: bool = True,
) -> RAGAgent:
    return RAGAgent(search_type=search_type, use_rerank=use_rerank)
