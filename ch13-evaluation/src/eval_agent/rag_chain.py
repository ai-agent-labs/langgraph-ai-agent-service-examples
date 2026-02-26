import os
from collections.abc import Iterator

from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langfuse import observe

from eval_agent.config import get_settings
from eval_agent.langfuse_setup import get_langfuse_client, get_langfuse_handler, init_langfuse

_vectorstore: FAISS | None = None


def _get_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key.get_secret_value(),
    )


def setup_sample_vectorstore() -> FAISS:
    global _vectorstore

    sample_docs = [
        Document(
            page_content="연차휴가는 입사 1년차에 15일이 부여됩니다. "
            "이후 매년 1일씩 추가되어 최대 25일까지 사용할 수 있습니다. "
            "연차휴가는 반일(0.5일) 단위로 사용 가능합니다.",
            metadata={"source": "휴가정책.pdf", "page": 1},
        ),
        Document(
            page_content="재택근무는 주 2일까지 가능합니다. "
            "재택근무를 신청하려면 최소 3일 전에 팀장 승인을 받아야 합니다. "
            "긴급한 경우 당일 신청도 가능하나 팀장 판단에 따릅니다.",
            metadata={"source": "근무정책.pdf", "page": 3},
        ),
        Document(
            page_content="출장비 정산은 출장 완료 후 7일 이내에 해야 합니다. "
            "영수증과 함께 경비정산 시스템에 등록하면 됩니다. "
            "숙박비는 1박당 15만원까지, 식비는 1일 5만원까지 지원됩니다.",
            metadata={"source": "출장정책.pdf", "page": 2},
        ),
        Document(
            page_content="병가는 연간 60일까지 사용할 수 있습니다. "
            "3일 이상 연속 병가 시 의사 진단서를 제출해야 합니다. "
            "병가 중에도 급여는 100% 지급됩니다.",
            metadata={"source": "휴가정책.pdf", "page": 5},
        ),
        Document(
            page_content="회의실 예약은 사내 인트라넷에서 할 수 있습니다. "
            "최대 2시간까지 예약 가능하며, 연장이 필요한 경우 "
            "다음 예약이 없을 때만 현장에서 연장할 수 있습니다.",
            metadata={"source": "시설이용안내.pdf", "page": 1},
        ),
    ]

    embeddings = _get_embeddings()
    _vectorstore = FAISS.from_documents(sample_docs, embeddings)

    return _vectorstore


def get_vectorstore() -> FAISS:
    global _vectorstore
    if _vectorstore is None:
        setup_sample_vectorstore()
    return _vectorstore


@observe()
def retrieve_documents(query: str, k: int | None = None) -> list[Document]:
    settings = get_settings()
    k = k or settings.search_top_k

    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    docs = retriever.invoke(query)
    return docs


@observe()
def generate_answer(query: str, context: str) -> str:
    settings = get_settings()
    handler = get_langfuse_handler()

    llm = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=0,
        api_key=settings.openai_api_key.get_secret_value(),
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """당신은 회사 정책 안내 도우미입니다.
주어진 문서만을 참고하여 질문에 답변하세요.

규칙:
1. 문서에 있는 내용만 답변하세요
2. 문서에 없는 내용은 "해당 정보는 문서에서 확인할 수 없습니다"라고 답변하세요
3. 친절하고 명확하게 답변하세요""",
            ),
            (
                "user",
                """[참고 문서]
{context}

[질문]
{query}""",
            ),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    config = {"callbacks": [handler]} if handler else {}
    response = chain.invoke({"context": context, "query": query}, config=config)

    return response


@observe()
def ask_rag(question: str) -> dict:
    # Langfuse 초기화 확인
    init_langfuse()

    # 1. 문서 검색
    docs = retrieve_documents(question)

    # 2. 컨텍스트 구성
    context = "\n\n".join(
        [f"[출처: {doc.metadata.get('source', '알 수 없음')}]\n{doc.page_content}" for doc in docs]
    )

    # 3. 답변 생성
    answer = generate_answer(question, context)

    # 4. 트레이스에 메타데이터 추가 (Langfuse가 활성화된 경우)
    langfuse = get_langfuse_client()
    if langfuse:
        langfuse.update_current_trace(
            input={"question": question},
            output={"answer": answer, "num_docs": len(docs)},
        )

    return {
        "answer": answer,
        "documents": docs,
        "context": context,
    }


class RAGAgent:
    def __init__(self):
        init_langfuse()
        self.history: list[dict[str, str]] = []
        self._trace_ids: list[str] = []

    def chat(self, question: str) -> str:
        result = ask_rag(question)
        answer = result["answer"]

        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": answer})

        return answer

    def stream(self, question: str) -> Iterator[str]:
        init_langfuse()
        handler = get_langfuse_handler()
        settings = get_settings()

        # 1. 문서 검색
        docs = retrieve_documents(question)
        context = "\n\n".join(
            [f"[출처: {doc.metadata.get('source', '알 수 없음')}]\n{doc.page_content}" for doc in docs]
        )

        # 2. LLM 스트리밍 응답
        llm = init_chat_model(
            model_provider="openai",
            model=settings.default_model,
            temperature=0,
            api_key=settings.openai_api_key.get_secret_value(),
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 회사 정책 안내 도우미입니다. 주어진 문서만을 참고하여 질문에 답변하세요.",
                ),
                ("user", "[참고 문서]\n{context}\n\n[질문]\n{query}"),
            ]
        )

        chain = prompt | llm | StrOutputParser()

        self.history.append({"role": "user", "content": question})

        full_response = ""
        config = {"callbacks": [handler]} if handler else {}
        for chunk in chain.stream({"context": context, "query": question}, config=config):
            full_response += chunk
            yield chunk

        self.history.append({"role": "assistant", "content": full_response})

    def clear_history(self) -> None:
        self.history = []
        self._trace_ids = []

    def get_history(self) -> list[dict[str, str]]:
        return self.history


def create_rag_agent() -> RAGAgent:
    return RAGAgent()
