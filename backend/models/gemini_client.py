# models/gemini_client.py

import os

from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """Thin wrapper around Google's Gemini API.

    If GEMINI_API_KEY is set, prompts go to Gemini (model from GEMINI_MODEL).
    Without a key the client runs in offline stub mode and echoes the prompt,
    so the API, routing and memory can be developed and tested with no credentials.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None
        if self.api_key:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        if self._client is None:
            return f"Gemini response for: {prompt}"
        response = self._client.models.generate_content(model=self.model, contents=prompt)
        return response.text
