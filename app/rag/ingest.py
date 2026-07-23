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
    Structure expected:
        knowledge/pdfs/ramayana/*.pdf
        knowledge/pdfs/mahabharata/*.pdf
    """
    documents: List[Document] = []

    # Load Ramayana
    ramayana_dir = KNOWLEDGE_DIR / "ramayana"
    documents.extend(load_pdfs_from_folder(ramayana_dir, "ramayana"))

    # Load Mahabharata
    mahabharata_dir = KNOWLEDGE_DIR / "mahabharata"
    documents.extend(load_pdfs_from_folder(mahabharata_dir, "mahabharata"))

    # Fallback: also check the root pdfs/ folder (for old structure)
    root_pdfs = list(KNOWLEDGE_DIR.glob("*.pdf")) + list(KNOWLEDGE_DIR.glob("*.PDF"))
    if root_pdfs:
        print(f"[Ingest] Also found {len(root_pdfs)} PDF(s) in root pdfs/ folder (legacy)")
        for pdf_path in root_pdfs:
            name_lower = pdf_path.name.lower()
            epic = "unknown"
            if "ramayan" in name_lower:
                epic = "ramayana"
            elif "mahabharat" in name_lower or "mb" in name_lower:
                epic = "mahabharata"

            try:
                text = extract_text_from_pdf(pdf_path)
                if text.strip():
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": pdf_path.name,
                                "epic": epic,
                                "file_path": str(pdf_path),
                            },
                        )
                    )
                    print(f"  → {pdf_path.name} | epic={epic}")
            except Exception as e:
                print(f"  → ERROR: {e}")

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
        print("  → Put PDFs in: knowledge/pdfs/ramayana/  or  knowledge/pdfs/mahabharata/")
        return 0

    chunks = chunk_documents(documents)

    vs = get_vectorstore()

    if reset:
        print("[Ingest] Reset requested — adding to existing collection (manual cleanup if needed)")

    # Add documents
    vs.add_documents(chunks)
    print(f"[Ingest] Successfully added {len(chunks)} chunks to vector store")
    return len(chunks)
