import json
import logging
from typing import Optional

import httpx

from .base import BaseAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    async def chat(self, prompt: str, system_prompt: str = "", json_mode: bool = False) -> str:
        payload = self._build_payload([{"role": "user", "content": prompt}], system_prompt, json_mode)
        return await self._execute_request(payload)

    async def chat_with_history(
        self, history: list[dict], system_prompt: str = "", json_mode: bool = False
    ) -> str:
        payload = self._build_payload(history, system_prompt, json_mode)
        return await self._execute_request(payload)

    def _build_payload(self, history: list[dict], system_prompt: str, json_mode: bool) -> dict:
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        payload = {"contents": contents}

        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        if json_mode:
            payload["generationConfig"] = {"responseMimeType": "application/json"}

        return payload

    async def _execute_request(self, payload: dict) -> str:
        headers = {"Content-Type": "application/json"}
        url = f"{self.base_url}?key={self.api_key}"

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if "candidates" in data and data["candidates"]:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                return ""
            except Exception as e:
                logger.error("Gemini API call failed: %s", e)
                raise
