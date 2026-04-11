# Chapter 4: 프롬프트 엔지니어링

> AI 에이전트 개발 기술서 4장 "프롬프트 엔지니어링" 실습 프로젝트입니다.

이 프로젝트는 책에서 소개하는 구조화 프롬프트, 페르소나, 사고 연쇄(CoT) 기법을 직접 실행해 볼 수 있는 예제를 담고 있습니다. 프롬프트 템플릿은 `prompts/` 디렉터리의 YAML 파일로 관리되어 코드와 분리되어 있습니다.

## 빠른 시작

```bash
cd ch04-prompt-engineering
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 설정

uv sync
uv run python run_email_summary.py
uv run python run_persona.py
uv run python run_cot.py
```

## 프로젝트 구조

```
ch04-prompt-engineering/
├── prompts/
│   ├── email_summary.yaml        # 4.2-3 구조화 프롬프트 (이메일 요약)
│   ├── persona_with_tone.yaml    # 4.3-1 페르소나 + 톤
│   └── with_cot.yaml             # 4.3-3 사고 연쇄(CoT)
├── src/
│   └── prompt_engineering/
│       └── __init__.py
├── run_email_summary.py          # 이메일 요약 실행
├── run_persona.py                # 페르소나 적용 실행
├── run_cot.py                    # CoT 실행
├── pyproject.toml
└── README.md
```

## 책과의 매핑

| 책 절 | 예제 | YAML | 실행 스크립트 |
|---|---|---|---|
| 4.2-3 | 구조화 프롬프트로 이메일 요약 | `prompts/email_summary.yaml` | `run_email_summary.py` |
| 4.3-1 | 페르소나 적용 | `prompts/persona_with_tone.yaml` | `run_persona.py` |
| 4.3-3 | 사고 연쇄(CoT) | `prompts/with_cot.yaml` | `run_cot.py` |

## YAML 템플릿이 별도 파일인 이유

책 L3081 TIP:

> 실무에서 사용되는 프롬프트는 예제에서 보았던 단순한 형태보다 훨씬 길고 복잡한 경우가 많습니다. 또, 둘 이상의 여러 프롬프트를 하나의 서비스에서 사용하는 경우도 빈번합니다. 따라서 코드 안에 프롬프트 문자열을 직접 작성하는 방식은 유지보수성과 재사용성 측면에서 매우 비효율적입니다.

YAML로 분리하면 코드와 프롬프트를 독립적으로 수정할 수 있고, 여러 서비스에서 재사용하기 편리합니다.

## 참고 자료

- [LangChain Prompt 공식 문서](https://python.langchain.com/docs/concepts/prompt_templates/)
- [load_prompt API](https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.loading.load_prompt.html)

---

**AI 에이전트 개발 기술서** - 4장 "프롬프트 엔지니어링" 실습 프로젝트
