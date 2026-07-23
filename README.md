# Itihasa Bot – Backend

Kid-friendly chatbot that teaches the **Ramayana** and **Mahabharata** using RAG over your PDF documents.

**Stack**
- FastAPI
- LangChain + Postgres (pgvector)
- LLMs: **Grok (xAI)** primary + **Gemini** fallback
- PDF extraction: PyMuPDF

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

Edit `.env` and add:
- `XAI_API_KEY` → from https://console.x.ai
- `GOOGLE_API_KEY` → from https://aistudio.google.com
- `DATABASE_URL` → your Render Postgres connection string (or local Postgres with pgvector)

### 3. Put your PDFs (separate folders)

```
knowledge/pdfs/
├── ramayana/          ← Put all Ramayana PDFs here
│   └── *.pdf
└── mahabharata/       ← Put all Mahabharata PDFs here
    └── *.pdf
```

Example:
```bash
cp /path/to/your/ramayana-*.pdf knowledge/pdfs/ramayana/
cp /path/to/your/mahabharata-*.pdf knowledge/pdfs/mahabharata/
```

### 4. Create the vector extension (one-time on Postgres)

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Ingest documents

```bash
python -m scripts.ingest_documents
```

### 6. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs to try the `/chat` endpoint.

---

## API

**POST /chat**

```json
{
  "message": "Who is Hanuman and what is he known for?",
  "history": [],
  "epic_filter": "ramayana",   // optional: "ramayana" | "mahabharata"
  "provider": "grok"           // optional: "grok" | "gemini"
}
```

---

## Project Structure

```
app/
├── api/chat.py          # Chat endpoint
├── llm/                 # Grok + Gemini + router
├── rag/                 # Ingest, retrieve, vectorstore
├── prompts/system.py    # Kid-safe system prompt
└── main.py
knowledge/pdfs/
├── ramayana/            # Your Ramayana PDFs
└── mahabharata/         # Your Mahabharata PDFs
scripts/ingest_documents.py
```

---

## Notes on large PDFs

Your largest file is ~89 MB. PyMuPDF handles this fine.  
Ingestion may take a few minutes the first time depending on total size and embedding rate limits.

---

## Next

- Frontend (separate repo)
- Character cards endpoint
- Better metadata / chapter-aware chunking
- Admin upload endpoint for new PDFs
