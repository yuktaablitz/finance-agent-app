"""
Gemini Integration Service
Handles all Gemini API calls with structured output parsing, retry logic,
rate limiting, and comprehensive error handling.
"""

import os
import json
import re
import logging
import asyncio
import time
from typing import Dict, Optional, Type, Any, Union, List
from functools import wraps
from datetime import datetime, timedelta

from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

try:
    # New SDK (preferred) - install via: pip install google-genai
    from google import genai as genai_v1
except Exception:
    genai_v1 = None

try:
    # Legacy SDK (fallback) - already in your requirements
    import google.generativeai as genai_legacy
except Exception:
    genai_legacy = None

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiError(Exception):
    """Custom exception for Gemini service errors."""
    pass


class RateLimitError(GeminiError):
    """Exception raised when rate limit is exceeded."""
    pass


class QuotaExceededError(GeminiError):
    """Exception raised when API quota is exceeded."""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on certain errors
                    if isinstance(e, (ValidationError, ValueError)):
                        raise
                    
                    if attempt < max_retries:
                        delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {str(e)}")
            
            raise last_exception
        return wrapper
    return decorator


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
 
        # Single locked default model. You can override via GEMINI_MODEL in backend/.env.
        self.model_name = os.getenv("GEMINI_MODEL", "models/gemini-3-flash-preview")
        
        # Rate limiting settings
        self.max_requests_per_minute = int(os.getenv("GEMINI_RATE_LIMIT", "60"))
        self.request_times: List[datetime] = []
        
        # Cache for simple requests
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl = int(os.getenv("GEMINI_CACHE_TTL", "300"))  # 5 minutes

        # Prefer the new SDK if available (this is what you'll want for "Gemini 3")
        if genai_v1 is not None:
            self._client: Any = genai_v1.Client(api_key=api_key)
            self._mode = "v1"
            logger.info(f"Initialized Gemini service with v1 SDK using model: {self.model_name}")
            return

        # Fallback to legacy SDK (older model name support)
        if genai_legacy is None:
            raise ImportError(
                "No Gemini SDK available. Install one of: google-genai (preferred) or google-generativeai."
            )

        genai_legacy.configure(api_key=api_key)
        self.model = genai_legacy.GenerativeModel(self.model_name)
        self._mode = "legacy"
        logger.info(f"Initialized Gemini service with legacy SDK using model: {self.model_name}")
    
    def _check_rate_limit(self) -> None:
        """Check if the current request would exceed rate limits."""
        now = datetime.now()
        
        # Clean old requests (older than 1 minute)
        self.request_times = [req_time for req_time in self.request_times 
                             if now - req_time < timedelta(minutes=1)]
        
        if len(self.request_times) >= self.max_requests_per_minute:
            raise RateLimitError(
                f"Rate limit exceeded: {self.max_requests_per_minute} requests per minute"
            )
        
        self.request_times.append(now)
    
    def _get_cache_key(self, system_prompt: str, user_query: str, temperature: float) -> str:
        """Generate a cache key for the request."""
        import hashlib
        content = f"{system_prompt}|{user_query}|{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available and not expired."""
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self._cache_ttl):
                logger.debug(f"Cache hit for key: {cache_key[:8]}...")
                return cached_data["response"]
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: Dict) -> None:
        """Cache the response for future use."""
        self._cache[cache_key] = {
            "response": response,
            "timestamp": datetime.now()
        }
        
        # Limit cache size to prevent memory issues
        if len(self._cache) > 100:
            # Remove oldest entries
            oldest_keys = sorted(self._cache.keys(), 
                               key=lambda k: self._cache[k]["timestamp"])[:10]
            for key in oldest_keys:
                del self._cache[key]

    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=30.0)
    async def generate_response(
        self,
        system_prompt: str,
        user_query: str,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate response from Gemini with optional structured output.
        
        Args:
            system_prompt: System prompt defining the AI's behavior
            user_query: The user's query/question
            response_schema: Optional Pydantic model for structured output
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Dict with 'response' and 'metadata' keys
            
        Raises:
            GeminiError: For API-related errors
            RateLimitError: When rate limits are exceeded
            ValidationError: When response validation fails
        """
        # Check cache first
        cache_key = self._get_cache_key(system_prompt, user_query, temperature)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Check rate limits
        self._check_rate_limit()
        
        full_prompt = f"""{system_prompt}

USER QUERY: {user_query}

IMPORTANT: You MUST respond in valid JSON format with this exact structure:
{{
    "response": "your natural language response here",
    "metadata": {{
        "agent": "agent_name",
        "confidence": 0.95,
        "personality_used": "personality_name",
        "context_factors": ["factor1", "factor2"],
        "suggested_action": "action_name",
        "related_transactions": ["txn_id1", "txn_id2"]
    }}
}}

Ensure your response is helpful, accurate, and follows the personality tone specified."""

        try:
            logger.info(f"Generating response for query: {user_query[:100]}...")
            response_text = await self._generate_content_text(full_prompt, temperature)
            
            # Try to parse as JSON
            parsed = self._extract_json(response_text)
            
            if parsed and "response" in parsed and "metadata" in parsed:
                # Validate the structure
                validated_response = self._validate_response_structure(parsed)
                
                # Cache the successful response
                self._cache_response(cache_key, validated_response)
                
                logger.info(f"Successfully generated and validated response")
                return validated_response
            else:
                # Fallback: wrap the response
                logger.warning("Failed to parse structured response, using fallback")
                fallback_response = {
                    "response": response_text,
                    "metadata": {
                        "agent": "general",
                        "confidence": 0.7,
                        "personality_used": "unknown",
                        "context_factors": ["parsing_failed"],
                        "suggested_action": None,
                        "related_transactions": None
                    }
                }
                self._cache_response(cache_key, fallback_response)
                return fallback_response
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            error_response = {
                "response": f"I encountered an error processing your request. Please try again. Error: {str(e)}",
                "metadata": {
                    "agent": "error",
                    "confidence": 0.0,
                    "personality_used": "none",
                    "context_factors": ["error_occurred"],
                    "suggested_action": "retry",
                    "related_transactions": None
                }
            }
            return error_response

    async def _generate_content_text(self, full_prompt: str, temperature: float) -> str:
        """Generate raw text from Gemini using the configured SDK."""
        try:
            if self._mode == "v1":
                resp = self._client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": 2048,
                    },
                )
                return getattr(resp, "text", None) or str(resp)

            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=genai_legacy.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise GeminiError(f"Failed to generate content: {str(e)}")

    def _validate_response_structure(self, response: Dict) -> Dict:
        """Validate and normalize the response structure."""
        try:
            # Ensure required fields exist
            if "response" not in response:
                response["response"] = "No response provided"
            
            if "metadata" not in response:
                response["metadata"] = {}
            
            metadata = response["metadata"]
            
            # Validate and normalize metadata fields
            metadata.setdefault("agent", "general")
            metadata.setdefault("confidence", 0.7)
            
            # Ensure confidence is a valid float between 0 and 1
            try:
                confidence = float(metadata["confidence"])
                metadata["confidence"] = max(0.0, min(1.0, confidence))
            except (ValueError, TypeError):
                metadata["confidence"] = 0.7
            
            metadata.setdefault("personality_used", "unknown")
            metadata.setdefault("context_factors", [])
            metadata.setdefault("suggested_action", None)
            metadata.setdefault("related_transactions", None)
            
            # Ensure context_factors is a list
            if not isinstance(metadata["context_factors"], list):
                metadata["context_factors"] = [str(metadata["context_factors"])]
            
            return response
            
        except Exception as e:
            logger.warning(f"Response validation failed: {str(e)}")
            # Return a safe fallback structure
            return {
                "response": response.get("response", "Validation failed"),
                "metadata": {
                    "agent": "general",
                    "confidence": 0.5,
                    "personality_used": "unknown",
                    "context_factors": ["validation_failed"],
                    "suggested_action": None,
                    "related_transactions": None
                }
            }

    async def list_available_models(self) -> Dict[str, Any]:
        """List models available for this API key (best-effort)."""
        try:
            if getattr(self, "_mode", None) == "v1":
                # google-genai
                models = []
                for m in self._client.models.list():
                    name = getattr(m, "name", None) or getattr(m, "model", None) or str(m)
                    models.append(name)
                return {
                    "sdk": "google-genai",
                    "configured_model": self.model_name,
                    "models": models,
                }

            # legacy google-generativeai
            models = await asyncio.to_thread(list, genai_legacy.list_models())
            model_names = [getattr(m, "name", str(m)) for m in models]
            
            return {
                "sdk": "google-generativeai",
                "configured_model": self.model_name,
                "models": model_names,
            }
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return {
                "sdk": "unknown",
                "configured_model": getattr(self, "model_name", None),
                "models": [],
                "error": str(e),
            }
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from response text with improved patterns."""
        if not text or not isinstance(text, str):
            return None
            
        text = text.strip()
        
        # Try multiple JSON extraction patterns
        patterns = [
            # Standard JSON object
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            # JSON with possible nested objects and arrays
            r'\{(?:[^{}]|\{[^{}]*\})*\}',
            # More permissive pattern for malformed JSON
            r'\{[\s\S]*?\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            
            for match in matches:
                try:
                    # Clean up the JSON string
                    cleaned_json = self._clean_json_string(match)
                    parsed = json.loads(cleaned_json)
                    
                    # Validate that it has the expected structure
                    if isinstance(parsed, dict) and ("response" in parsed or "metadata" in parsed):
                        logger.debug(f"Successfully extracted JSON using pattern: {pattern[:30]}...")
                        return parsed
                        
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON decode failed for match: {str(e)}")
                    continue
        
        # Try parsing the entire text as JSON
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        
        logger.warning("Failed to extract valid JSON from response")
        return None
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean and normalize a JSON string for parsing."""
        # Remove common issues
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
        json_str = re.sub(r'\n+', ' ', json_str)    # Replace newlines with spaces
        json_str = re.sub(r'\s+', ' ', json_str)    # Normalize whitespace
        
        # Fix unescaped quotes in JSON strings (common issue)
        # This is a simplified fix - may need refinement for complex cases
        json_str = re.sub(r'(?<!\\)"(?=[^,:}\]]*?[^,:}\]])(?=[^,:}\]]*?[^,:}\]])', r'\"', json_str)
        
        return json_str.strip()
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of the Gemini service."""
        return {
            "status": "healthy",
            "mode": getattr(self, "_mode", "unknown"),
            "model": getattr(self, "model_name", "unknown"),
            "rate_limit": {
                "max_requests_per_minute": self.max_requests_per_minute,
                "current_requests": len(self.request_times),
            },
            "cache": {
                "size": len(self._cache),
                "ttl_seconds": self._cache_ttl,
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()
        logger.info("Response cache cleared")
    
    def update_rate_limit(self, max_requests_per_minute: int) -> None:
        """Update the rate limit configuration."""
        self.max_requests_per_minute = max(1, max_requests_per_minute)
        logger.info(f"Rate limit updated to {self.max_requests_per_minute} requests per minute")


# Singleton instance
gemini_service = GeminiService()
