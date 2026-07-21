import logging
from typing import Optional, Any

from .providers.factory import AIProviderFactory
from .providers.base import BaseAIProvider
from .prompt_builder import PromptBuilder
from .context_builder import ContextBuilder
from .response_validator import ResponseValidator, ResponseParser

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """Coordinates context, prompts, validation, and AI provider calls."""
    
    def __init__(self, provider_name: str = "gemini", fallback_provider_name: str = "mistral"):
        self.provider: Optional[BaseAIProvider] = AIProviderFactory.get_provider(provider_name)
        self.fallback_provider: Optional[BaseAIProvider] = AIProviderFactory.get_provider(fallback_provider_name)

    def is_available(self) -> bool:
        return self.provider is not None or self.fallback_provider is not None
        
    async def _execute_with_retry(self, provider: BaseAIProvider, task_prompt: str, system_prompt: str, json_mode: bool) -> str:
        from tenacity import retry, stop_after_attempt, wait_exponential
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        async def _call():
            return await provider.chat(prompt=task_prompt, system_prompt=system_prompt, json_mode=json_mode)
            
        return await _call()

    async def execute_task(
        self,
        task_prompt: str,
        template_name: str,
        context_data: dict = None,
        raw_context: str = None,
        json_mode: bool = False,
        **kwargs
    ) -> Any:
        """General executor for AI tasks with fallback."""
        if not self.is_available():
            return self._mock_fallback(template_name)
            
        context_str = ""
        if raw_context:
            context_str = raw_context
        elif context_data:
            context_str = ContextBuilder.build_user_context(**context_data)
            
        system_prompt = PromptBuilder.build(template_name, context=context_str, **kwargs)
        
        response_text = None
        
        # Try primary
        if self.provider:
            try:
                response_text = await self._execute_with_retry(self.provider, task_prompt, system_prompt, json_mode)
            except Exception as e:
                logger.warning(f"Primary provider failed: {e}. Trying fallback.")
                
        # Try fallback
        if not response_text and self.fallback_provider:
            try:
                response_text = await self._execute_with_retry(self.fallback_provider, task_prompt, system_prompt, json_mode)
            except Exception as e:
                logger.error(f"Fallback provider failed: {e}")
                
        if not response_text:
            return self._mock_fallback(template_name)
            
        if json_mode:
            parsed = ResponseValidator.validate_json(response_text)
            if not parsed:
                logger.error("Failed to parse JSON response from AI")
                return self._mock_fallback(template_name)
            return parsed
            
        return response_text
            
    async def chat_session(self, history: list[dict], template_name: str, context_data: dict = None, raw_context: str = None) -> str:
        """Executes a multi-turn chat with fallback."""
        if not self.is_available():
            return "I am running in mock mode. Please configure an API key to enable live chat."
            
        context_str = ""
        if raw_context:
            context_str = raw_context
        elif context_data:
            context_str = ContextBuilder.build_user_context(**context_data)
            
        system_prompt = PromptBuilder.build(template_name, context=context_str)
        
        # We don't retry chats heavily as they are synchronous to user
        if self.provider:
            try:
                return await self.provider.chat_with_history(history, system_prompt=system_prompt)
            except Exception as e:
                logger.warning(f"Primary provider failed in chat: {e}. Trying fallback.")
                
        if self.fallback_provider:
            try:
                return await self.fallback_provider.chat_with_history(history, system_prompt=system_prompt)
            except Exception as e:
                logger.error(f"Fallback provider failed in chat: {e}")
                
        return "I encountered an error trying to process that."

    def _mock_fallback(self, template_name: str) -> Any:
        """Returns mock data depending on the requested task."""
        if template_name == "resume":
            return {"skills": ["Python", "Linux"], "projects": [], "certifications": []}
        elif template_name == "resume_profile":
            return {
                "full_name": None, "email": None, "phone": None, "location": None,
                "summary": None, "education": [], "experience": [],
                "skills": [], "projects": [], "certifications": [],
                "urls": {"github": [], "linkedin": [], "portfolio": [], "personal_website": [], "other": []}
            }
        elif template_name == "quiz":
            return {"questions": [
                {"question": "What is Linux?", "options": ["OS", "Browser", "Language", "Fruit"], "correct_index": 0, "explanation": "It's an OS"}
            ]}
        elif template_name == "mission":
            return {"task": "Review your notes on network fundamentals", "skill": "Networking", "estimated_minutes": 30, "priority": "medium"}
        elif template_name == "summarize":
            return {"summary": "Session summary placeholder", "important_facts": [], "next_goal": ""}
        return "This is a mock response (API key missing)."
