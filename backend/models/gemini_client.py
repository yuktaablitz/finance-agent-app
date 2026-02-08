import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """Gemini 3 Flash Preview client with advanced reasoning capabilities."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("Missing GEMINI_API_KEY in .env")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3-flash-preview"

    def generate(self, prompt: str, thinking_level: str = "high") -> str:
        """Generate content with Gemini 3 Flash.
        
        Args:
            prompt: The input prompt
            thinking_level: 'minimal', 'low', 'medium', or 'high' (default)
                          - minimal: No thinking, fastest response
                          - low: Minimal reasoning, fast
                          - medium: Balanced thinking
                          - high: Maximum reasoning depth (default)
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level=thinking_level)
            )
        )
        return response.text

    def extract_transaction_from_receipt(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
        """Extract transaction from receipt using Gemini 3 multimodal with high-resolution OCR.
        
        Uses media_resolution_high for optimal text extraction from receipts.
        """
        prompt = (
            "Extract transaction details from this receipt. "
            "Return ONLY valid JSON with this exact schema:\n"
            "{\n"
            "  \"amount\": number,\n"
            "  \"currency\": string,\n"
            "  \"merchant\": string,\n"
            "  \"date\": string (YYYY-MM-DD),\n"
            "  \"category\": string,\n"
            "  \"description\": string\n"
            "}\n"
            "If a field is unknown, use null (except amount: use 0)."
        )

        try:
            # Use Gemini 3 with high-resolution media processing for receipt OCR
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=prompt),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime_type,
                                    data=image_bytes,
                                ),
                                media_resolution={"level": "media_resolution_high"}
                            )
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="medium")
                )
            )
            text = response.text
        except Exception as e:
            print(f"Receipt extraction error: {e}")
            text = "{}"

        parsed = self._extract_json(text)
        if isinstance(parsed, dict):
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
            "description": text.strip()[:500] if text else None,
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
