# My AI Agent - 2장 실습 프로젝트

> AI 에이전트 개발 기술서 2장 "개발 시작하기" 실습 프로젝트입니다.

이 프로젝트는 LangChain을 사용해 간단한 대화형 AI 에이전트를 구현합니다.

## 목차

- [요구사항](#요구사항)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [사용 방법](#사용-방법)
- [설정](#설정)
- [문제 해결](#문제-해결)

## 요구사항

- **Python**: 3.11 이상
- **패키지 관리자**: [uv](https://docs.astral.sh/uv/) (권장) 또는 pip
- **API 키**: OpenAI

## 빠른 시작

### 1. uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 프로젝트 설정

```bash
# 저장소 클론 또는 디렉토리 이동
cd ch02-getting-started

# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
```

### 3. API 키 설정

`.env` 파일을 열고 API 키를 입력합니다:

```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-proj-your-actual-api-key
```

### 4. 실행

```bash
# 웹 UI 실행
uv run streamlit run app.py
```

## 프로젝트 구조

```
ch02-getting-started/
├── src/
│   └── my_agent/
│       ├── __init__.py      # 패키지 초기화
│       ├── agent.py         # 에이전트 로직
│       └── config.py        # 설정 관리
├── .env.example             # 환경변수 템플릿
├── .gitignore               # Git 제외 파일
├── .python-version          # Python 버전
├── app.py                   # Streamlit 웹 앱
├── pyproject.toml           # 프로젝트 설정
└── README.md                # 이 파일
```

## 사용 방법

### 웹 UI (Streamlit)

```bash
uv run streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속합니다.

**기능:**

- 실시간 스트리밍 응답
- 모델 선택
- 커스텀 시스템 프롬프트
- 대화 기록 관리

### Python 코드에서 사용

```python
from my_agent import create_agent

# 에이전트 생성
agent = create_agent()

# 대화
response = agent.chat("안녕하세요!")
print(response)

# 스트리밍 응답
for chunk in agent.stream("Python에 대해 알려주세요"):
    print(chunk, end="", flush=True)
```

## 설정

### 환경변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `DEFAULT_MODEL` | 기본 모델 | `gpt-5.2` |
| `DEBUG` | 디버그 모드 | `false` |

### 지원 모델

- `gpt-5.2` (권장)

## 문제 해결

### API 키 오류

```
ValueError: OPENAI_API_KEY가 설정되지 않았습니다.
```

**해결:** `.env` 파일에 API 키가 올바르게 설정되어 있는지 확인하세요.

### 모듈 찾을 수 없음

```
ModuleNotFoundError: No module named 'my_agent'
```

**해결:** 프로젝트 루트에서 실행하고 있는지 확인하세요:
```bash
cd ch02-getting-started
uv sync
```

### Streamlit 포트 충돌

```
Port 8501 is already in use
```

**해결:** 다른 포트 사용:
```bash
uv run streamlit run app.py --server.port 8502
```

## 참고 자료

- [LangChain 공식 문서](https://python.langchain.com/)
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [uv 공식 문서](https://docs.astral.sh/uv/)

## 라이선스

MIT License

---

**AI 에이전트 개발 기술서** - 2장 "개발 시작하기" 실습 프로젝트
