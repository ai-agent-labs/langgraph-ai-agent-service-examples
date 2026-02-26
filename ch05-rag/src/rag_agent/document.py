from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_agent.config import get_settings


def create_text_splitter(
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> RecursiveCharacterTextSplitter:
    settings = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.chunk_size,
        chunk_overlap=chunk_overlap or settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
        length_function=len,
    )


def load_text_file(file_path: str | Path) -> Document:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    return Document(page_content=content, metadata={"source": str(path.name)})


def chunk_text(
    text: str,
    source: str = "unknown",
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    splitter = create_text_splitter(chunk_size, chunk_overlap)
    doc = Document(page_content=text, metadata={"source": source})
    chunks = splitter.split_documents([doc])

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    return chunks


def chunk_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    splitter = create_text_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    return chunks


# 샘플 문서 데이터 (실습용)
SAMPLE_DOCUMENTS = [
    """
# 넥스트랩 휴가 정책 (2025년 11월 개정)

## 1. 연차휴가

### 1.1 부여 기준
- 입사 1년 미만: 매월 1일씩 부여 (최대 11일)
- 입사 1년 이상: 연 15일 일괄 부여
- 3년 이상 근속 시 매 2년마다 1일 추가 (최대 25일)

### 1.2 사용 방법
- HR 시스템에서 최소 3일 전 신청
- 반차(0.5일) 단위로 사용 가능
- 미사용 연차는 다음 해로 이월 불가 (단, 연말 5일까지 이월 가능)

## 2. 특별휴가

### 2.1 경조사 휴가
- 본인 결혼: 5일
- 자녀 결혼: 1일
- 배우자/본인 부모 사망: 5일
- 조부모/형제자매 사망: 3일

### 2.2 출산/육아 휴가
- 출산휴가: 90일 (산전후휴가)
- 배우자 출산휴가: 10일
- 육아휴직: 최대 1년 (만 8세 이하 자녀)
""",
    """
# 넥스트랩 재택근무 정책 (2025년 11월 개정)

## 1. 재택근무 기본 원칙

### 1.1 적용 대상
- 전 직원 적용 (수습기간 제외)
- 업무 특성상 현장 근무가 필요한 경우 예외

### 1.2 재택근무 가능 일수
- 주 3일까지 재택근무 가능
- 매주 화요일은 전사 출근일 (팀 미팅)

## 2. 신청 및 승인

### 2.1 신청 방법
- HR 시스템에서 최소 하루 전 신청
- 자동 승인 (특별 프로젝트 기간 제외)

### 2.2 취소/변경
- 당일 취소 가능 (오전 9시 전)
- 긴급 상황 시 팀장에게 직접 연락

## 3. 근무 환경

### 3.1 필수 조건
- 안정적인 인터넷 환경
- 업무용 노트북 지참
- 슬랙/줌 접속 가능 상태 유지

### 3.2 근무 시간
- 코어 타임: 10:00 ~ 16:00
- 점심시간: 12:00 ~ 13:00
- 나머지 시간은 유연 근무
""",
    """
# 넥스트랩 비용 정산 가이드 (2025년 11월)

## 1. 정산 가능 항목

### 1.1 업무 관련 비용
- 출장 교통비 (대중교통, 택시)
- 출장 숙박비 (1박 최대 15만원)
- 고객 미팅 식대 (인당 3만원 한도)

### 1.2 자기개발비
- 업무 관련 도서 구매 (월 5만원 한도)
- 온라인 강의 수강료 (연 50만원 한도)
- 자격증 응시료 (사전 승인 필요)

## 2. 정산 절차

### 2.1 증빙 서류
- 영수증 또는 카드 매출전표
- 전자 영수증 가능 (이메일 첨부)
- 간이영수증은 3만원 이하만 인정

### 2.2 제출 방법
- 경비 정산 시스템에서 신청
- 증빙 서류 스캔 또는 사진 첨부
- 매월 말일까지 당월 비용 제출

### 2.3 지급
- 익월 급여일에 급여와 함께 지급
- 법인카드 사용 시 별도 정산 불필요
""",
]


def get_sample_documents() -> list[Document]:
    sources = ["휴가정책.md", "재택근무정책.md", "비용정산가이드.md"]
    return [
        Document(page_content=text.strip(), metadata={"source": source})
        for text, source in zip(SAMPLE_DOCUMENTS, sources)
    ]


def get_sample_chunks() -> list[Document]:
    documents = get_sample_documents()
    return chunk_documents(documents)
