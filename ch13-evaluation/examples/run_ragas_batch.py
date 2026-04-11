"""
책 13.3절 "배치 평가" 실습 스크립트.

사용법::

    cd ch13-evaluation
    uv sync                   # ragas / datasets 설치
    uv run python examples/run_ragas_batch.py

``.env`` 파일에 ``OPENAI_API_KEY`` 가 설정되어 있어야 한다.
"""

from __future__ import annotations

from dotenv import load_dotenv

from eval_agent.ragas_eval import evaluate_rag_batch

load_dotenv()


SAMPLES = [
    {
        "question": "재택근무는 며칠까지 가능한가요?",
        "answer": "재택근무는 주 2회까지 가능하며, 전날 17시까지 신청해야 합니다.",
        "contexts": [
            "재택근무는 주 2회까지 가능하며, 전날 17시까지 신청해야 합니다.",
        ],
        "ground_truth": "재택근무는 주 2회까지 가능하며 전날 17시까지 신청",
    },
    {
        "question": "건강검진은 언제 신청할 수 있나요?",
        "answer": "건강검진은 매년 상반기(3~6월)에 신청 가능하며, 복지 포털에서 예약할 수 있습니다.",
        "contexts": [
            "건강검진: 한도 50만원, 상반기(3-6월)에 복지 포털에서 예약",
            "건강검진 신청은 복지 포털을 통해 진행됩니다.",
        ],
        "ground_truth": "건강검진은 상반기에 복지 포털에서 예약",
    },
    {
        "question": "경조사 휴가는 며칠인가요?",
        "answer": "경조사 휴가는 본인 결혼 5일, 자녀 결혼 1일, 부모 사망 5일이 부여됩니다.",
        "contexts": [
            "경조사 휴가는 본인 결혼 5일, 자녀 결혼 1일, 부모 사망 5일.",
        ],
        "ground_truth": "본인 결혼 5일, 자녀 결혼 1일, 부모 사망 5일",
    },
]


def main() -> None:
    print(f"[RAGAS] 배치 평가 시작 — 샘플 {len(SAMPLES)}건")
    result = evaluate_rag_batch(SAMPLES)

    print("\n== 샘플별 점수 ==")
    try:
        print(result.to_pandas())
    except Exception:
        print(result)

    print("\n== 지표별 평균 ==")
    scores = getattr(result, "scores", None)
    if scores:
        for metric, value in scores.items():
            print(f"  {metric}: {value:.3f}")


if __name__ == "__main__":
    main()
