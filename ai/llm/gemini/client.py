"""Google Gemini client (alternative LLM).

Used when only a Google AI Studio API key is available. It exposes the same
``generate_response`` / ``generate_json`` interface as the Grok client so the
RAG pipeline and the extraction step can use either provider unchanged.

The API key lives on the backend / AI layer only and is never exposed to the
frontend.
"""

import json
import re
from typing import Optional

import httpx

from ai.config.settings import settings


DEFAULT_SYSTEM_PROMPT = (
    "You are an Indian legal information assistant. "
    "Explain legal information clearly and accurately. "
    "Never invent laws, sections, citations or legal procedures. "
    "If the provided context does not contain the answer, say so. "
    "This system provides legal information, not legal advice."
)


class GeminiClient:
    """Thin wrapper around the Google Gemini generateContent API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):

        self.api_key = api_key or settings.GEMINI_API_KEY

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your project .env file."
            )

        self.model = model or settings.GEMINI_MODEL
        self.temperature = settings.GROK_TEMPERATURE
        self.max_tokens = settings.GROK_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT_SECONDS

    # --- Public interface (mirrors GrokClient) --------------------------

    def generate_response(
        self,
        prompt: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a free-form text response from Gemini."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        return self._generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=False,
        )

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        temperature: Optional[float] = None,
    ) -> dict:
        """Generate a JSON object response and parse it into a dict."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        content = self._generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=None,
            json_mode=True,
        )

        return self._parse_json(content)

    # --- Internals ------------------------------------------------------

    def _generate(
        self,
        prompt: str,
        system_prompt: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        json_mode: bool,
    ) -> str:

        url = f"{settings.GEMINI_BASE_URL}/{self.model}:generateContent"

        generation_config = {
            "temperature": (
                self.temperature if temperature is None else temperature
            ),
            "maxOutputTokens": max_tokens or self.max_tokens,
        }

        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]},
            ],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": generation_config,
        }

        try:
            response = httpx.post(
                url,
                params={"key": self.api_key},
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

        except httpx.HTTPStatusError as error:
            raise RuntimeError(
                "Gemini API request failed: "
                f"{error.response.status_code} {error.response.text}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                f"Gemini API request failed: {error}"
            ) from error

        return self._extract_text(data)

    @staticmethod
    def _extract_text(data: dict) -> str:
        """Pull the generated text out of a Gemini response payload."""

        candidates = data.get("candidates") or []

        if not candidates:
            blocked = (data.get("promptFeedback") or {}).get(
                "blockReason"
            )
            raise ValueError(
                "Gemini returned no candidates"
                + (f" (blocked: {blocked})" if blocked else ".")
            )

        parts = (candidates[0].get("content") or {}).get("parts") or []

        text = "".join(part.get("text", "") for part in parts)

        if not text.strip():
            raise ValueError("Gemini returned an empty response.")

        return text

    @staticmethod
    def _parse_json(content: str) -> dict:
        """Parse model output into JSON, tolerating code fences."""

        if not content:
            raise ValueError("Gemini returned an empty response.")

        text = content.strip()

        fence_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)

        if fence_match:
            text = fence_match.group(1).strip()

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            brace_match = re.search(r"\{.*\}", text, re.DOTALL)

            if brace_match:
                return json.loads(brace_match.group(0))

            raise ValueError(
                "Gemini response could not be parsed as JSON."
            )
