# Itihasa Bot – Backend

Kid-friendly chatbot that teaches the **Ramayana** and **Mahabharata** using RAG over your PDF documents.

**Stack**
- FastAPI
- LangChain + **Chroma** (local vector store)
- LLMs: **Grok (xAI)** primary + **Gemini** fallback
- PDF extraction: PyMuPDF

> Note: We are currently using Chroma (file-based) so you don’t need Postgres.  
> We can switch back to Postgres + pgvector later when deploying to Render.

---

## Quick Start (Local)

### 1. Setup

```bash
cd itihasa-bot-backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment

```bash
cp .env.example .env
```

Edit `.env` and add your real keys:
- `XAI_API_KEY` → from https://console.x.ai
- `GOOGLE_API_KEY` → from https://aistudio.google.com (must start with `AIzaSy...`)

### 3. Put your PDFs

```
knowledge/pdfs/
├── ramayana/          ← Ramayana PDFs
└── mahabharata/       ← Mahabharata PDFs
```

### 4. Ingest documents

```bash
python -m scripts.ingest_documents
```

This will create a local Chroma database in `data/chroma/`.

### 5. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs

---

## Notes

- Some PDFs may return empty text (they are scanned images). We can add OCR later.
- First ingestion of large books can take several minutes because of embedding.
