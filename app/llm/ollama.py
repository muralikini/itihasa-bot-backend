"""
Ollama local LLM client (OpenAI-compatible API).
"""

from typing import List

from openai import OpenAI

from app.config import get_settings


class OllamaClient:
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(
            api_key="ollama",  # required by the client but ignored by Ollama
            base_url="http://localhost:11434/v1",
        )
        # Change this if you pulled a different model
        self.model = getattr(settings, "ollama_model", "llama3.2")

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
