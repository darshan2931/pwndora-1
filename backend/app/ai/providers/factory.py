import os
import logging
from typing import Optional

from .base import BaseAIProvider
from .gemini import GeminiProvider
from .mistral import MistralProvider

logger = logging.getLogger(__name__)

class AIProviderFactory:
    """Factory to instantiate the appropriate AI provider based on environment variables."""
    
    @staticmethod
    def get_provider(provider_name: str = "gemini") -> Optional[BaseAIProvider]:
        if provider_name == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not found in environment.")
                return None
            return GeminiProvider(api_key=api_key)
            
        elif provider_name == "mistral":
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                logger.warning("MISTRAL_API_KEY not found in environment.")
                return None
            return MistralProvider(api_key=api_key)
            
        else:
            logger.error(f"Unknown AI provider requested: {provider_name}")
            return None
