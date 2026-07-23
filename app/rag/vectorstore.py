"""
Chroma vector store helpers using LangChain.
Local file-based vector database – no Postgres required.
"""

from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import get_settings


# Persist Chroma DB here
CHROMA_DIR = Path(__file__).resolve().parents[2] / "data" / "chroma"


def get_embeddings():
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )


def get_vectorstore(collection_name: str = "itihasa_docs") -> Chroma:
    """
    Returns a persistent Chroma vector store.
    Creates the directory if it does not exist.
    """
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )


def similarity_search(
    query: str,
    k: int = 6,
    filter: Optional[dict] = None,
) -> List[Document]:
    vs = get_vectorstore()

    if filter:
        return vs.similarity_search(query, k=k, filter=filter)
    return vs.similarity_search(query, k=k)
