"""
PDF ingestion pipeline for Ramayana & Mahabharata documents.
Supports separate folders: knowledge/pdfs/ramayana/ and knowledge/pdfs/mahabharata/
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


def load_pdfs_from_folder(folder: Path, epic: str) -> List[Document]:
    """Load all PDFs from a specific epic folder."""
    documents: List[Document] = []

    if not folder.exists():
        print(f"[Ingest] Folder not found: {folder}")
        return documents

    pdf_files = list(folder.glob("*.pdf")) + list(folder.glob("*.PDF"))
    print(f"[Ingest] Found {len(pdf_files)} PDF(s) in {epic}/")

    for pdf_path in pdf_files:
        print(f"[Ingest] Processing: {pdf_path.name} ...")
        try:
            text = extract_text_from_pdf(pdf_path)
            if not text.strip():
                print(f"  → Empty text, skipping")
                continue

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


def load_all_pdfs() -> List[Document]:
    """
    Load PDFs from both epic folders.
    """
    documents: List[Document] = []

    # Load Ramayana
    ramayana_dir = KNOWLEDGE_DIR / "ramayana"
    documents.extend(load_pdfs_from_folder(ramayana_dir, "ramayana"))

    # Load Mahabharata
    mahabharata_dir = KNOWLEDGE_DIR / "mahabharata"
    documents.extend(load_pdfs_from_folder(mahabharata_dir, "mahabharata"))

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
    Adds documents in batches to avoid Chroma max batch size limit.
    """
    documents = load_all_pdfs()
    if not documents:
        print("[Ingest] No documents to ingest.")
        print("  → Put PDFs in: knowledge/pdfs/ramayana/  or  knowledge/pdfs/mahabharata/")
        return 0

    chunks = chunk_documents(documents)

    vs = get_vectorstore()

    if reset:
        print("[Ingest] Reset requested — adding to existing collection")

    # Chroma has a max batch size (~5000). We use a safe smaller size.
    BATCH_SIZE = 500
    total = len(chunks)
    added = 0

    print(f"[Ingest] Adding {total} chunks in batches of {BATCH_SIZE} ...")

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        vs.add_documents(batch)
        added += len(batch)
        print(f"  → Added batch {i // BATCH_SIZE + 1}: {added}/{total} chunks")

    print(f"[Ingest] Successfully added {added} chunks to vector store")
    return added
