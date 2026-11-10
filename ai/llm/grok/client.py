"""xAI Grok client.

Grok (xAI) is the ONLY large language model used by this system. It performs
legal information extraction and answer generation. The API key lives on the
backend/AI layer only and is never exposed to the frontend.
"""

import json
import re
from typing import Optional

from openai import OpenAI

from ai.config.settings import settings


DEFAULT_SYSTEM_PROMPT = (
    "You are an Indian legal information assistant. "
    "Explain legal information clearly and accurately. "
    "Never invent laws, sections, citations or legal procedures. "
    "If the provided context does not contain the answer, say so. "
    "This system provides legal information, not legal advice."
)


class GrokClient:
    """Thin wrapper around the xAI Grok chat completion API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):

        self.api_key = api_key or settings.XAI_API_KEY

        if not self.api_key:
            raise ValueError(
                "XAI_API_KEY is not configured. "
                "Add it to your project .env file."
            )

        self.model = model or settings.GROK_MODEL
        self.temperature = settings.GROK_TEMPERATURE
        self.max_tokens = settings.GROK_MAX_TOKENS

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=settings.GROK_BASE_URL,
        )

    def generate_response(
        self,
        prompt: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a free-form text response from Grok."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=(
                    self.temperature
                    if temperature is None
                    else temperature
                ),
                max_tokens=max_tokens or self.max_tokens,
            )

            return response.choices[0].message.content

        except Exception as error:
            raise RuntimeError(
                f"LLM API request failed: {error}"
            ) from error

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        temperature: Optional[float] = None,
    ) -> dict:
        """Generate a JSON object response and parse it into a dict."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=(
                    self.temperature
                    if temperature is None
                    else temperature
                ),
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

        except Exception as error:
            raise RuntimeError(
                f"LLM JSON request failed: {error}"
            ) from error

        return self._parse_json(content)

    @staticmethod
    def _parse_json(content: str) -> dict:
        """Parse model output into JSON, tolerating code fences."""

        if not content:
            raise ValueError("LLM returned an empty response.")

        text = content.strip()

        # Strip markdown code fences if present.
        fence_match = re.search(
            r"```(?:json)?\s*(.*?)```",
            text,
            re.DOTALL,
        )

        if fence_match:
            text = fence_match.group(1).strip()

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            # Fall back to the first {...} block.
            brace_match = re.search(r"\{.*\}", text, re.DOTALL)

            if brace_match:
                return json.loads(brace_match.group(0))

            raise ValueError(
                "LLM response could not be parsed as JSON."
            )
