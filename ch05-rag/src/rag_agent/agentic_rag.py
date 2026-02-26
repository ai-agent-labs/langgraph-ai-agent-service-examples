import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph

from rag_agent.rag_chain import create_llm
from rag_agent.reranker import search_with_rerank


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    question: str
    context: str
    search_count: int
    search_queries: list[str]


def should_search(state: AgentState) -> str:
    # 최대 검색 횟수 제한
    if state["search_count"] >= 3:
        return "answer"

    # 첫 검색은 무조건 수행
    if state["search_count"] == 0:
        return "search"

    # LLM이 추가 검색 필요 여부 판단
    llm = create_llm()

    prompt = ChatPromptTemplate.from_template(
        """질문: {question}

현재까지 수집된 정보:
{context}

이 정보로 질문에 충분히 답변할 수 있나요?
- 충분하면 "ANSWER"
- 추가 정보가 필요하면 "SEARCH"

한 단어로만 답하세요."""
    )

    chain = prompt | llm | StrOutputParser()
    decision = chain.invoke(
        {"question": state["question"], "context": state["context"]}
    )

    return "search" if "SEARCH" in decision.upper() else "answer"


def generate_search_query(state: AgentState) -> str:
    # 첫 검색은 원래 질문 사용
    if state["search_count"] == 0:
        return state["question"]

    # LLM이 새로운 검색 쿼리 생성
    llm = create_llm()

    prompt = ChatPromptTemplate.from_template(
        """원래 질문: {question}

이미 검색한 쿼리들:
{previous_queries}

현재까지 수집된 정보:
{context}

아직 답변에 부족한 정보를 찾기 위한 새로운 검색 쿼리를 생성하세요.
검색 쿼리만 출력하세요."""
    )

    chain = prompt | llm | StrOutputParser()
    return chain.invoke(
        {
            "question": state["question"],
            "previous_queries": "\n".join(state["search_queries"]),
            "context": state["context"],
        }
    )


def search_node(state: AgentState) -> dict:
    # 검색 쿼리 생성
    search_query = generate_search_query(state)

    # 검색 수행 (하이브리드 + 리랭킹)
    results = search_with_rerank(search_query, initial_k=10, final_k=3)

    # 새로운 컨텍스트 추가
    new_context = "\n\n".join([r["content"] for r in results])
    combined_context = state["context"]
    if combined_context:
        combined_context += "\n\n---\n\n" + new_context
    else:
        combined_context = new_context

    return {
        "context": combined_context,
        "search_count": state["search_count"] + 1,
        "search_queries": state["search_queries"] + [search_query],
        "messages": [],
    }


def answer_node(state: AgentState) -> dict:
    llm = create_llm()

    prompt = ChatPromptTemplate.from_template(
        """다음 정보를 바탕으로 질문에 답변하세요.
정보에 없는 내용은 "확인할 수 없습니다"라고 답하세요.
답변 끝에 참고한 정보의 출처를 명시하세요.

[수집된 정보]
{context}

[질문]
{question}

[답변]"""
    )

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": state["context"], "question": state["question"]})

    return {"messages": [AIMessage(content=answer)]}


def create_agentic_rag_graph() -> StateGraph:
    # 그래프 정의
    workflow = StateGraph(AgentState)

    # 노드 추가
    workflow.add_node("search", search_node)
    workflow.add_node("answer", answer_node)

    # 엣지 설정
    workflow.set_entry_point("search")

    # 조건부 엣지: 검색 후 추가 검색 또는 답변
    workflow.add_conditional_edges(
        "search",
        should_search,
        {
            "search": "search",
            "answer": "answer",
        },
    )

    # 답변 후 종료
    workflow.add_edge("answer", END)

    return workflow.compile()


def ask_agentic_rag(question: str) -> str:
    graph = create_agentic_rag_graph()

    result = graph.invoke(
        {
            "question": question,
            "messages": [],
            "context": "",
            "search_count": 0,
            "search_queries": [],
        }
    )

    # 마지막 메시지(AI 답변) 반환
    if result["messages"]:
        return result["messages"][-1].text
    return "답변을 생성할 수 없습니다."


class AgenticRAGAgent:
    def __init__(self):
        self.graph = create_agentic_rag_graph()
        self.history: list[dict[str, str]] = []

    def chat(self, question: str) -> str:
        result = self.graph.invoke(
            {
                "question": question,
                "messages": [],
                "context": "",
                "search_count": 0,
                "search_queries": [],
            }
        )

        answer = (
            result["messages"][-1].text
            if result["messages"]
            else "답변을 생성할 수 없습니다."
        )

        # 대화 기록 저장
        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": answer})

        return answer

    def clear_history(self) -> None:
        self.history = []

    def get_history(self) -> list[dict[str, str]]:
        return self.history


def create_agentic_rag_agent() -> AgenticRAGAgent:
    return AgenticRAGAgent()
