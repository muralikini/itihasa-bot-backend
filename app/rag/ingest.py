"""
PDF ingestion pipeline for Ramayana & Mahabharata documents.
"""

from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.rag.vectorstore import get_vectorstore


KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "pdfs"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract clean text from a PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    texts = []
    for page in doc:
        text = page.get_text("text")
        if text and text.strip():
            texts.append(text.strip())
    doc.close()
    return "\n\n".join(texts)


def load_all_pdfs() -> List[Document]:
    """Load every PDF in knowledge/pdfs/ and return LangChain Documents."""
    documents: List[Document] = []

    if not KNOWLEDGE_DIR.exists():
        print(f"[Ingest] Knowledge directory not found: {KNOWLEDGE_DIR}")
        return documents

    pdf_files = list(KNOWLEDGE_DIR.glob("*.pdf")) + list(KNOWLEDGE_DIR.glob("*.PDF"))
    print(f"[Ingest] Found {len(pdf_files)} PDF(s)")

    for pdf_path in pdf_files:
        print(f"[Ingest] Processing: {pdf_path.name} ...")
        try:
            text = extract_text_from_pdf(pdf_path)
            if not text.strip():
                print(f"  → Empty text, skipping")
                continue

            # Simple metadata guessing from filename
            name_lower = pdf_path.name.lower()
            epic = "unknown"
            if "ramayan" in name_lower or "ramayana" in name_lower:
                epic = "ramayana"
            elif "mahabharat" in name_lower or "mahabharata" in name_lower or "mb" in name_lower:
                epic = "mahabharata"

            doc = Document(
                page_content=text,
                metadata={
                    "source": pdf_path.name,
                    "epic": epic,
                    "file_path": str(pdf_path),
                },
            )
            documents.append(doc)
            print(f"  → Extracted ~{len(text):,} characters | epic={epic}")
        except Exception as e:
            print(f"  → ERROR processing {pdf_path.name}: {e}")

    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"[Ingest] Created {len(chunks)} chunks")
    return chunks


def ingest_all(reset: bool = False) -> int:
    """
    Full ingestion pipeline.
    Returns number of chunks added.
    """
    documents = load_all_pdfs()
    if not documents:
        print("[Ingest] No documents to ingest.")
        return 0

    chunks = chunk_documents(documents)

    vs = get_vectorstore()

    if reset:
        print("[Ingest] Reset requested — adding to existing collection (manual cleanup if needed)")

    # Add documents
    vs.add_documents(chunks)
    print(f"[Ingest] Successfully added {len(chunks)} chunks to vector store")
    return len(chunks)
