"""
Retriever helper – gets relevant context for a user question.
"""

from typing import List, Optional

from langchain_core.documents import Document

from app.config import get_settings
from app.rag.vectorstore import similarity_search


def retrieve_context(
    query: str,
    epic_filter: Optional[str] = None,
    k: Optional[int] = None,
) -> str:
    """
    Retrieve relevant chunks and format them as a single context string.
    """
    settings = get_settings()
    top_k = k or settings.top_k

    filter_dict = None
    if epic_filter and epic_filter.lower() in ("ramayana", "mahabharata"):
        filter_dict = {"epic": epic_filter.lower()}

    docs: List[Document] = similarity_search(query, k=top_k, filter=filter_dict)

    if not docs:
        return ""

    # Format context with source attribution
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        epic = doc.metadata.get("epic", "")
        header = f"[Source {i}: {source}"
        if epic:
            header += f" | {epic.title()}"
        header += "]"
        parts.append(f"{header}\n{doc.page_content.strip()}")

    return "\n\n---\n\n".join(parts)
