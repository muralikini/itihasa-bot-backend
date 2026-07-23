"""
xAI Grok client (OpenAI-compatible API).
"""

from typing import List, Optional

from openai import OpenAI

from app.config import get_settings


class GrokClient:
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(
            api_key=settings.xai_api_key,
            base_url="https://api.x.ai/v1",
        )
        self.model = "grok-3"  # or grok-3-mini / grok-4 when available

    def chat(
        self,
        messages: List[dict],
        temperature: float = 0.6,
        max_tokens: int = 1024,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
