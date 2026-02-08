import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise Exception("Missing GEMINI_API_KEY in .env")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    def generate(self, prompt: str) -> str:

        response = self.model.generate_content(prompt)

        return response.text

    def extract_transaction_from_receipt(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
        """Extract a structured cash transaction from a receipt image.

        Returns a dict with keys like: amount, merchant, date, category, currency, description.
        Best-effort parsing: if model returns non-JSON, falls back to a minimal dict.
        """

        prompt = (
            "You are a receipt understanding system. Extract the transaction from the image. "
            "Return ONLY valid JSON with this schema:\n"
            "{\n"
            "  \"amount\": number,\n"
            "  \"currency\": string,\n"
            "  \"merchant\": string,\n"
            "  \"date\": string,\n"
            "  \"category\": string,\n"
            "  \"description\": string\n"
            "}\n"
            "If a field is unknown, use null (except amount: use 0)."
        )

        try:
            response = self.model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": mime_type,
                        "data": image_bytes,
                    },
                ]
            )
            text = getattr(response, "text", None) or ""
        except Exception:
            # As a fallback, ask text-only (still returns something for demo purposes).
            text = self.generate(prompt)

        parsed = self._extract_json(text)
        if isinstance(parsed, dict):
            # Normalize minimal fields
            parsed.setdefault("amount", 0)
            parsed.setdefault("currency", None)
            parsed.setdefault("merchant", None)
            parsed.setdefault("date", None)
            parsed.setdefault("category", None)
            parsed.setdefault("description", None)
            return parsed

        return {
            "amount": 0,
            "currency": None,
            "merchant": None,
            "date": None,
            "category": None,
            "description": text.strip()[:500] if isinstance(text, str) else None,
        }

    def _extract_json(self, text: str):
        if not text or not isinstance(text, str):
            return None

        text = text.strip()

        # Try whole-string JSON first
        try:
            return json.loads(text)
        except Exception:
            pass

        # Extract first JSON object
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return None

        candidate = m.group(0)
        # Remove trailing commas
        candidate = re.sub(r",\s*}", "}", candidate)
        candidate = re.sub(r",\s*]", "]", candidate)

        try:
            return json.loads(candidate)
        except Exception:
            return None
