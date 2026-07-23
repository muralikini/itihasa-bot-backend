from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.llm.router import LLMRouter
from app.rag.retriever import retrieve_context

router = APIRouter(prefix="/chat", tags=["chat"])

llm_router = LLMRouter()


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[ChatMessage]] = []
    epic_filter: Optional[str] = Field(
        None, description="Optional: 'ramayana' or 'mahabharata'"
    )
    provider: Optional[str] = Field(
        None, description="Force 'grok' or 'gemini'"
    )


class ChatResponse(BaseModel):
    answer: str
    provider: str
    sources_used: bool


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. Retrieve relevant context
        context = retrieve_context(
            query=request.message,
            epic_filter=request.epic_filter,
        )

        # 2. Convert history
        history = [{"role": m.role, "content": m.content} for m in (request.history or [])]

        # 3. Generate answer
        result = llm_router.generate(
            user_message=request.message,
            context=context,
            chat_history=history,
            force_provider=request.provider,
        )

        return ChatResponse(
            answer=result["answer"],
            provider=result["provider"],
            sources_used=bool(context),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
