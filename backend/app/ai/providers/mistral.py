import logging
from typing import Optional

import httpx

from .base import BaseAIProvider

logger = logging.getLogger(__name__)


class MistralProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str = "mistral-small-latest"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.mistral.ai/v1/chat/completions"

    async def chat(self, prompt: str, system_prompt: str = "", json_mode: bool = False) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self._execute_request(messages, json_mode)

    async def chat_with_history(
        self, history: list[dict], system_prompt: str = "", json_mode: bool = False
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        return await self._execute_request(messages, json_mode)

    async def _execute_request(self, messages: list[dict], json_mode: bool) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(self.base_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
                return ""
            except Exception as e:
                logger.error("Mistral API call failed: %s", e)
                raise
