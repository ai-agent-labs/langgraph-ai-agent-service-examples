import os
import uuid

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from eval_agent.config import get_settings
from eval_agent.langfuse_setup import (
    get_langfuse_client,
    get_langfuse_handler,
    init_langfuse,
    is_langfuse_enabled,
)


def create_score(
    trace_id: str,
    name: str,
    value: float | int,
    data_type: str = "NUMERIC",
    comment: str | None = None,
) -> None:
    init_langfuse()
    langfuse = get_langfuse_client()

    if langfuse is None:
        return

    langfuse.create_score(
        trace_id=trace_id,
        name=name,
        value=value,
        data_type=data_type,
        comment=comment,
    )


def evaluate_faithfulness(
    answer: str,
    context: str,
    trace_id: str | None = None,
) -> dict:
    init_langfuse()
    settings = get_settings()
    handler = get_langfuse_handler()

    llm = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=0,
        api_key=settings.openai_api_key.get_secret_value(),
    )

    # 1단계: 답변에서 주장 추출
    extract_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """다음 답변에서 사실적 주장을 추출하세요.
각 주장을 한 줄에 하나씩 작성하세요.
주장이 없으면 "주장 없음"이라고 작성하세요.""",
            ),
            ("user", "답변: {answer}"),
        ]
    )

    extract_chain = extract_prompt | llm | StrOutputParser()
    config = {"callbacks": [handler]} if handler else {}
    claims_text = extract_chain.invoke({"answer": answer}, config=config)

    claims = [c.strip() for c in claims_text.strip().split("\n") if c.strip()]

    if not claims or claims[0] == "주장 없음":
        result = {
            "score": 1.0,
            "explanation": "답변에 검증 가능한 주장이 없습니다.",
            "claims": [],
        }
        if trace_id:
            create_score(trace_id, "faithfulness", 1.0, comment=result["explanation"])
        return result

    # 2단계: 각 주장이 컨텍스트에서 지원되는지 확인
    verify_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """주어진 컨텍스트가 주장을 지원하는지 판단하세요.
"예" 또는 "아니오"로만 답변하세요.""",
            ),
            (
                "user",
                """컨텍스트: {context}

주장: {claim}

이 주장은 컨텍스트에서 지원됩니까?""",
            ),
        ]
    )

    verify_chain = verify_prompt | llm | StrOutputParser()

    supported_count = 0
    verified_claims = []

    for claim in claims:
        result_text = verify_chain.invoke(
            {"context": context, "claim": claim},
            config=config,
        )

        is_supported = "예" in result_text.lower() or "yes" in result_text.lower()
        verified_claims.append({"claim": claim, "supported": is_supported})

        if is_supported:
            supported_count += 1

    # 점수 계산
    score = supported_count / len(claims) if claims else 1.0

    result = {
        "score": score,
        "explanation": f"{len(claims)}개 주장 중 {supported_count}개가 컨텍스트에서 지원됨",
        "claims": verified_claims,
    }

    # Langfuse에 점수 기록
    if trace_id:
        create_score(trace_id, "faithfulness", score, comment=result["explanation"])

    return result


def evaluate_response(
    question: str,
    answer: str,
    context: str,
    trace_id: str | None = None,
) -> dict:
    init_langfuse()
    settings = get_settings()
    handler = get_langfuse_handler()

    llm = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=0,
        api_key=settings.openai_api_key.get_secret_value(),
    )

    # 1. Faithfulness 평가
    faithfulness_result = evaluate_faithfulness(answer, context)

    # 2. Answer Relevance 평가 (간단 버전)
    relevance_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """질문에 대한 답변의 관련성을 0~10점으로 평가하세요.

평가 기준:
- 10점: 질문에 정확하고 완전하게 답변
- 7-9점: 대체로 관련 있지만 일부 부족
- 4-6점: 부분적으로만 관련됨
- 1-3점: 거의 관련 없음
- 0점: 전혀 관련 없음

점수만 숫자로 답변하세요.""",
            ),
            (
                "user",
                """질문: {question}
답변: {answer}

관련성 점수:""",
            ),
        ]
    )

    relevance_chain = relevance_prompt | llm | StrOutputParser()
    config = {"callbacks": [handler]} if handler else {}
    relevance_text = relevance_chain.invoke(
        {"question": question, "answer": answer},
        config=config,
    )

    try:
        relevance_score = float(relevance_text.strip()) / 10.0
        relevance_score = max(0.0, min(1.0, relevance_score))
    except ValueError:
        relevance_score = 0.5

    # 전체 점수 계산 (가중 평균)
    overall_score = 0.6 * faithfulness_result["score"] + 0.4 * relevance_score

    result = {
        "faithfulness": faithfulness_result["score"],
        "relevance": relevance_score,
        "overall": overall_score,
        "details": {
            "faithfulness_details": faithfulness_result,
        },
    }

    # Langfuse에 점수 기록
    if trace_id:
        create_score(trace_id, "relevance", relevance_score)
        create_score(trace_id, "overall", overall_score)

    return result


def generate_trace_id() -> str:
    return str(uuid.uuid4())
