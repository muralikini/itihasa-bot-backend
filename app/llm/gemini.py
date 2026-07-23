"""
Google Gemini client.
"""

from typing import List

import google.generativeai as genai

from app.config import get_settings


class GeminiClient:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.google_api_key)
        # Prefer the latest stable model. Change if needed.
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def chat(
        self,
        messages: List[dict],
        temperature: float = 0.6,
        max_tokens: int = 1024,
    ) -> str:
        # Convert OpenAI-style messages to Gemini format
        system_instruction = None
        history = []
        user_content = ""

        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                system_instruction = content
            elif role == "user":
                user_content = content
            elif role == "assistant":
                history.append({"role": "model", "parts": [content]})

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_instruction,
        )

        chat = model.start_chat(history=history)
        response = chat.send_message(
            user_content,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text or ""
