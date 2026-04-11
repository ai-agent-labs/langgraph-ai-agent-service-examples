"""
RAGAS 기반 배치 평가 래퍼.

책 13.3절 "배치 평가"는 여러 질문-답변 샘플을 모아 한 번에 평가하는 방법을
다룬다. 본 모듈은 ``ragas`` 라이브러리의 ``evaluate`` 함수를 감싸, 샘플
리스트만 주면 Faithfulness / Answer Relevancy / Context Precision /
Context Recall 네 가지 지표를 한 번에 계산해 돌려준다.

사용 예::

    from eval_agent.ragas_eval import evaluate_rag_batch

    samples = [
        {
            "question": "재택근무는 며칠까지 가능한가요?",
            "answer": "재택근무는 주 2회까지 가능합니다.",
            "contexts": [
                "재택근무는 주 2회까지 가능하며, 전날 17시까지 신청해야 합니다."
            ],
            "ground_truth": "재택근무는 주 2회까지 가능",
        },
        ...
    ]
    result = evaluate_rag_batch(samples)
    print(result.to_pandas())

런타임 의존성: ``ragas``, ``datasets``.
"""

from __future__ import annotations

from typing import Any


def _build_dataset(samples: list[dict[str, Any]]):
    """샘플 리스트를 RAGAS가 기대하는 ``Dataset`` 형태로 변환."""
    from datasets import Dataset

    required = {"question", "answer", "contexts", "ground_truth"}
    for i, s in enumerate(samples):
        missing = required - set(s.keys())
        if missing:
            raise ValueError(
                f"samples[{i}]에 다음 키가 없습니다: {sorted(missing)}"
            )
        if not isinstance(s["contexts"], list):
            raise TypeError(
                f"samples[{i}]['contexts']는 list[str]이어야 합니다"
            )

    return Dataset.from_list(
        [
            {
                "question": s["question"],
                "answer": s["answer"],
                "contexts": s["contexts"],
                "ground_truth": s["ground_truth"],
            }
            for s in samples
        ]
    )


def evaluate_rag_batch(
    samples: list[dict[str, Any]],
    metrics: list[Any] | None = None,
):
    """RAGAS로 RAG 샘플 배치를 평가한다.

    Parameters
    ----------
    samples:
        각 샘플은 ``question``, ``answer``, ``contexts``(list[str]),
        ``ground_truth`` 네 키를 가져야 한다.
    metrics:
        평가 지표 리스트. ``None``이면 기본값(faithfulness, answer_relevancy,
        context_precision, context_recall)을 사용.

    Returns
    -------
    ``ragas.evaluation.EvaluationResult`` — ``.to_pandas()`` 로 DataFrame 변환,
    개별 점수는 ``result.scores`` 에서 확인.
    """
    from ragas import evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    if metrics is None:
        metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]

    dataset = _build_dataset(samples)
    return evaluate(dataset=dataset, metrics=metrics)
