import json
import logging
import time
from collections import OrderedDict
from typing import Optional

import httpx

from ai.demo_data import get_demo_response

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
TIMEOUT_SECONDS = 45

CACHE_TTL = 300
MAX_CACHE_SIZE = 500

_response_cache: OrderedDict[str, tuple[str, float]] = OrderedDict()


def _cache_key(prefix: str, *args) -> str:
    import hashlib
    raw = f"{prefix}:{':'.join(str(a) for a in args)}"
    return hashlib.md5(raw.encode()).hexdigest()


class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_keys: list[str], model: str = "gemini-2.0-flash"):
        if not api_keys:
            raise ValueError("At least one Gemini API key must be provided")
        self.api_keys = api_keys
        self.current_key_idx = 0
        self.model = model

    def _get_next_api_key(self) -> str:
        key = self.api_keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        return key

    def _build_contents(self, messages: list[dict]) -> tuple[list[dict], Optional[dict]]:
        contents = []
        system_instruction = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = {"parts": [{"text": content}]}
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": content}]})
            else:
                contents.append({"role": "user", "parts": [{"text": content}]})

        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hello"}]}]

        if contents[0].get("role") != "user":
            contents.insert(0, {"role": "user", "parts": [{"text": "Please respond based on the context provided."}]})

        return contents, system_instruction

    async def chat(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self._call_api(messages)

    async def chat_with_history(self, history: list[dict], system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        return await self._call_api(messages)

    async def _call_api(self, messages: list[dict]) -> str:
        contents, system_instruction = self._build_contents(messages)
        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                current_key = self._get_next_api_key()
                url = f"{self.BASE_URL}/models/{self.model}:generateContent?key={current_key}"

                payload: dict = {
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1024,
                        "topP": 0.9,
                        "topK": 40,
                    },
                }
                if system_instruction:
                    payload["systemInstruction"] = system_instruction

                async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                    resp = await client.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json=payload,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise ValueError("No candidates in Gemini response")

                    parts = candidates[0].get("content", {}).get("parts", [])
                    if not parts:
                        raise ValueError("No parts in Gemini response")

                    return parts[0].get("text", "")

            except (httpx.HTTPStatusError, httpx.RequestError, ValueError, KeyError) as e:
                last_error = e
                logger.warning(
                    "Gemini API call failed (attempt %d/%d): %s",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    e,
                )

        raise RuntimeError(f"Gemini API failed after {MAX_RETRIES + 1} attempts. Last error: {last_error}")
