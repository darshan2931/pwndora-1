import logging
import time
from collections import OrderedDict
from typing import Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
TIMEOUT_SECONDS = 60

CACHE_TTL = 300
MAX_CACHE_SIZE = 500

_response_cache: OrderedDict[str, tuple[str, float]] = OrderedDict()


def _cache_key(prefix: str, *args) -> str:
    import hashlib
    raw = f"{prefix}:{':'.join(str(a) for a in args)}"
    return hashlib.md5(raw.encode()).hexdigest()


class GeminiClient:
    """Gemini client using the official google-generativeai SDK."""

    def __init__(self, api_keys: list[str], model: str = "gemini-2.0-flash"):
        if not api_keys:
            raise ValueError("At least one Gemini API key must be provided")
        self.api_keys = api_keys
        self.current_key_idx = 0
        self.model_name = model
        # Configure with the first key
        self._configure_key(self.api_keys[0])

    def _configure_key(self, key: str):
        """Configure the SDK with the given API key."""
        genai.configure(api_key=key)

    def _get_next_api_key(self) -> str:
        key = self.api_keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        return key

    def _get_model(self, system_prompt: str = "") -> genai.GenerativeModel:
        """Create a GenerativeModel instance with optional system instruction."""
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024,
            top_p=0.9,
            top_k=40,
        )

        kwargs = {
            "model_name": self.model_name,
            "generation_config": generation_config,
        }
        if system_prompt:
            kwargs["system_instruction"] = system_prompt

        return genai.GenerativeModel(**kwargs)

    async def chat(self, prompt: str, system_prompt: str = "") -> str:
        """Send a single-turn chat message."""
        messages = [{"role": "user", "parts": [prompt]}]
        return await self._call_api(messages, system_prompt)

    async def chat_with_history(self, history: list[dict], system_prompt: str = "") -> str:
        """Send a multi-turn chat with history."""
        messages = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                # System messages go into system_instruction, not history
                if not system_prompt:
                    system_prompt = content
                continue
            gemini_role = "model" if role == "assistant" else "user"
            messages.append({"role": gemini_role, "parts": [content]})

        # Gemini requires the first message to be from user
        if messages and messages[0].get("role") != "user":
            messages.insert(0, {"role": "user", "parts": ["Please respond based on the context provided."]})

        # Gemini requires alternating user/model messages
        messages = self._fix_consecutive_roles(messages)

        if not messages:
            messages = [{"role": "user", "parts": ["Hello"]}]

        return await self._call_api(messages, system_prompt)

    def _fix_consecutive_roles(self, messages: list[dict]) -> list[dict]:
        """Merge consecutive messages with the same role (Gemini requires alternating)."""
        if not messages:
            return messages

        fixed = [messages[0]]
        for msg in messages[1:]:
            if msg["role"] == fixed[-1]["role"]:
                # Merge parts into the previous message
                fixed[-1]["parts"].extend(msg["parts"])
            else:
                fixed.append(msg)
        return fixed

    async def _call_api(self, messages: list[dict], system_prompt: str = "") -> str:
        """Call the Gemini API with retry logic and key rotation."""
        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                current_key = self._get_next_api_key()
                self._configure_key(current_key)

                model = self._get_model(system_prompt)

                # Use generate_content_async for async support
                response = await model.generate_content_async(
                    contents=messages,
                    request_options={"timeout": TIMEOUT_SECONDS},
                )

                if response.text:
                    return response.text

                # Handle blocked responses
                if response.candidates:
                    candidate = response.candidates[0]
                    if candidate.finish_reason and candidate.finish_reason.name == "SAFETY":
                        logger.warning("Gemini response blocked by safety filters")
                        return "I apologize, but I'm unable to provide a response to that question. Could you try rephrasing it?"

                raise ValueError("Empty response from Gemini API")

            except Exception as e:
                last_error = e
                error_str = str(e)
                logger.warning(
                    "Gemini API call failed (attempt %d/%d): %s",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    error_str,
                )

                # If rate limited, wait before retrying
                if "429" in error_str or "ResourceExhausted" in error_str:
                    wait_time = min(2 ** attempt, 10)
                    logger.info("Rate limited, waiting %ds before retry...", wait_time)
                    import asyncio
                    await asyncio.sleep(wait_time)
                elif "InvalidArgument" in error_str or "API_KEY_INVALID" in error_str:
                    logger.error("Invalid Gemini API key. Please check your GEMINI_API_KEY.")
                    break  # Don't retry on invalid key

        raise RuntimeError(f"Gemini API failed after {MAX_RETRIES + 1} attempts. Last error: {last_error}")
