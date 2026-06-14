"""
Shared Ollama client with connection pooling and structured output support.
"""
import json
import logging
from typing import Any, Optional
import aiohttp
from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Shared Ollama HTTP client with connection reuse and structured JSON output."""

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._available: Optional[bool] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def is_available(self) -> bool:
        """Check if Ollama is reachable (cached after first check)."""
        if self._available is not None:
            return self._available
        try:
            session = await self._get_session()
            async with session.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                self._available = resp.status == 200
        except Exception:
            self._available = False
        return self._available

    async def generate(
        self,
        prompt: str,
        *,
        timeout: int = 30,
        seed: int = 42,
    ) -> str:
        """Call Ollama /api/generate and return the raw response text."""
        session = await self._get_session()
        async with session.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "seed": seed,
                },
            },
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            result = await resp.json()
            return result.get("response", "")

    async def generate_json(
        self,
        prompt: str,
        *,
        timeout: int = 30,
        seed: int = 42,
    ) -> Optional[dict[str, Any]]:
        """Call Ollama and parse the response as JSON.

        Uses Ollama's format:"json" parameter for structured output,
        with a fallback to manual extraction.
        """
        session = await self._get_session()
        async with session.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "seed": seed,
                },
            },
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            result = await resp.json()
            text = result.get("response", "")

            # Primary: direct parse (Ollama format:"json" guarantees valid JSON)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

            # Fallback: extract JSON substring
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass

            logger.warning("Failed to parse Ollama response as JSON: %s", text[:200])
            return None


ollama_client = OllamaClient()
