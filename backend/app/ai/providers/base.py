from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """Abstract base class for all AI providers."""

    @abstractmethod
    async def chat(self, prompt: str, system_prompt: str = "", json_mode: bool = False) -> str:
        """
        Send a single prompt to the AI and return the response.
        If json_mode is True, the provider should attempt to return raw JSON.
        """
        pass

    @abstractmethod
    async def chat_with_history(
        self, history: list[dict], system_prompt: str = "", json_mode: bool = False
    ) -> str:
        """
        Send a conversation history to the AI and return the response.
        history format: [{"role": "user"|"assistant", "content": "..."}]
        """
        pass

    async def run_ocr(self, file_path: str) -> str:
        """
        Extract text from a file using OCR capabilities of the provider.
        """
        raise NotImplementedError("OCR is not supported by this provider.")

