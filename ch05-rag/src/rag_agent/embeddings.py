import os

import numpy as np
from langchain_openai import OpenAIEmbeddings

from rag_agent.config import get_settings


def create_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()
    return OpenAIEmbeddings(model=settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = create_embeddings()
    return embeddings.embed_documents(texts)


def embed_query(query: str) -> list[float]:
    embeddings = create_embeddings()
    return embeddings.embed_query(query)


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    a = np.array(v1)
    b = np.array(v2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
