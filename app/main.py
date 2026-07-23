from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Itihasa Bot API",
    description="Kid-friendly Ramayana & Mahabharata chatbot powered by RAG + Grok/Gemini",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "name": "Itihasa Bot API",
        "status": "running",
        "docs": "/docs",
        "primary_llm": settings.primary_llm,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
