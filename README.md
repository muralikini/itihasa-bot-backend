# Itihasa Bot – Backend

Kid-friendly chatbot that teaches the **Ramayana** and **Mahabharata** using RAG over your PDF documents.

**Current Stack**
- FastAPI
- LangChain + **Chroma** (local vector store)
- **Local embeddings** (`all-MiniLM-L6-v2`) – no embedding API cost
- LLMs for answers: **Grok (xAI)** primary + **Gemini** fallback
- PDF extraction: PyMuPDF

---

## Quick Start

```bash
cd itihasa-bot-backend
python -m venv .venv
.\.​venv\Scripts\Activate          # Windows
pip install -r requirements.txt
```

### Environment

```bash
copy .env.example .env
```

Add your keys (only needed for the chat answers, not for embeddings):
```env
XAI_API_KEY=...
GOOGLE_API_KEY=...
```

### Put PDFs

```
knowledge/pdfs/ramayana/
knowledge/pdfs/mahabharata/
```

### Ingest

```bash
python -m scripts.ingest_documents
```

First run will download the small embedding model (~80 MB) and then process the books.  
This can take 10–30 minutes depending on your machine because we have very large PDFs.

### Run API

```bash
uvicorn app.main:app --reload --port 8000
```
