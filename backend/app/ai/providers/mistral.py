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

    async def run_ocr(self, file_path: str) -> str:
        import os
        filename = os.path.basename(file_path)
        upload_url = "https://api.mistral.ai/v1/files"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=60) as client:
            # 1. Upload the file
            with open(file_path, "rb") as f:
                files = {"file": (filename, f)}
                data = {"purpose": "ocr"}
                resp = await client.post(upload_url, headers=headers, files=files, data=data)
                resp.raise_for_status()
                file_info = resp.json()
                file_id = file_info["id"]

            try:
                # 2. Get signed URL
                url_endpoint = f"https://api.mistral.ai/v1/files/{file_id}/url"
                resp = await client.get(url_endpoint, headers=headers)
                resp.raise_for_status()
                url_info = resp.json()
                signed_url = url_info["url"]

                # 3. Process OCR
                ocr_endpoint = "https://api.mistral.ai/v1/ocr"
                ocr_payload = {
                    "model": "mistral-ocr-latest",
                    "document": {
                        "type": "document_url",
                        "document_url": signed_url
                    }
                }
                resp = await client.post(ocr_endpoint, headers=headers, json=ocr_payload)
                resp.raise_for_status()
                ocr_data = resp.json()

                # 4. Extract markdown content
                pages = ocr_data.get("pages", [])
                ocr_text = "\n".join([page.get("markdown", "") for page in pages])
                return ocr_text
            finally:
                # Clean up uploaded file
                try:
                    delete_endpoint = f"https://api.mistral.ai/v1/files/{file_id}"
                    await client.delete(delete_endpoint, headers=headers)
                except Exception as delete_error:
                    logger.warning("Failed to delete temp file from Mistral: %s", delete_error)

