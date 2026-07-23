"""
Chroma vector store with local embeddings (no Google/OpenAI API needed for embeddings).
"""

from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import get_settings


# Persist Chroma DB here
CHROMA_DIR = Path(__file__).resolve().parents[2] / "data" / "chroma"


def get_embeddings():
    """
    Local embedding model – runs on your machine.
    all-MiniLM-L6-v2 is small, fast and good enough for this use case.
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},          # use "cuda" if you have a GPU
        encode_kwargs={"normalize_embeddings": True},
    )


def get_vectorstore(collection_name: str = "itihasa_docs") -> Chroma:
    """
    Returns a persistent Chroma vector store.
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
