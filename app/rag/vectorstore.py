"""
Postgres + pgvector vector store helpers using LangChain.
"""

from typing import List, Optional

from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import get_settings


def get_embeddings():
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )


def get_vectorstore(collection_name: str = "itihasa_docs") -> PGVector:
    settings = get_settings()
    embeddings = get_embeddings()

    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=settings.database_url,
        use_jsonb=True,
    )


def similarity_search(
    query: str,
    k: int = 6,
    filter: Optional[dict] = None,
) -> List[Document]:
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k, filter=filter)
