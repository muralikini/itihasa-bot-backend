"""
LLM Router: Ollama (local) primary, with Grok and Gemini as fallbacks.
"""

from typing import List, Optional

from app.config import get_settings
from app.llm.ollama import OllamaClient
from app.llm.grok import GrokClient
from app.llm.gemini import GeminiClient
from app.prompts.system import SYSTEM_PROMPT


class LLMRouter:
    def __init__(self):
        self.settings = get_settings()
        self.ollama = OllamaClient()
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
        Generate a response.
        Priority: force_provider → primary_llm → ollama → grok → gemini
        """
        provider = (force_provider or self.settings.primary_llm or "ollama").lower()

        messages = self._build_messages(user_message, context, chat_history)

        # Try the requested provider first, then fall back in order
        providers_to_try = [provider]
        for p in ["ollama", "grok", "gemini"]:
            if p not in providers_to_try:
                providers_to_try.append(p)

        last_error = None
        for p in providers_to_try:
            try:
                if p == "ollama":
                    answer = self.ollama.chat(messages)
                elif p == "grok":
                    answer = self.grok.chat(messages)
                elif p == "gemini":
                    answer = self.gemini.chat(messages)
                else:
                    continue
                return {"answer": answer, "provider": p}
            except Exception as e:
                print(f"[LLM Router] {p} failed: {e}")
                last_error = e
                continue

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

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
            for turn in chat_history[-6:]:
                messages.append(turn)

        messages.append({"role": "user", "content": user_message})
        return messages
