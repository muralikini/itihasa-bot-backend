"""
LLM Router: chooses Grok (primary) or Gemini (fallback).
"""

from typing import List, Optional

from app.config import get_settings
from app.llm.grok import GrokClient
from app.llm.gemini import GeminiClient
from app.prompts.system import SYSTEM_PROMPT


class LLMRouter:
    def __init__(self):
        self.settings = get_settings()
        self.grok = GrokClient()
        self.gemini = GeminiClient()

    def generate(
        self,
        user_message: str,
        context: str = "",
        chat_history: Optional[List[dict]] = None,
        force_provider: Optional[str] = None,
    ) -> dict:
        """
        Generate a response using the preferred LLM.
        Returns: {"answer": str, "provider": str}
        """
        provider = (force_provider or self.settings.primary_llm).lower()

        messages = self._build_messages(user_message, context, chat_history)

        try:
            if provider == "gemini":
                answer = self.gemini.chat(messages)
                used = "gemini"
            else:
                answer = self.grok.chat(messages)
                used = "grok"
        except Exception as e:
            # Automatic fallback
            print(f"[LLM Router] {provider} failed: {e}. Falling back...")
            if provider == "grok":
                answer = self.gemini.chat(messages)
                used = "gemini (fallback)"
            else:
                answer = self.grok.chat(messages)
                used = "grok (fallback)"

        return {"answer": answer, "provider": used}

    def _build_messages(
        self,
        user_message: str,
        context: str,
        chat_history: Optional[List[dict]],
    ) -> List[dict]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Here is relevant information from the sacred texts "
                        "(use this to answer accurately):\n\n" + context
                    ),
                }
            )

        if chat_history:
            # Keep last 6 turns max for context window
            for turn in chat_history[-6:]:
                messages.append(turn)

        messages.append({"role": "user", "content": user_message})
        return messages
