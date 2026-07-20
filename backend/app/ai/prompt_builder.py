import logging
import os
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"
logger = logging.getLogger(__name__)

class PromptBuilder:
    """Loads markdown prompt templates and renders them with variables."""
    
    @staticmethod
    def _load_template(name: str) -> str:
        path = PROMPTS_DIR / f"{name}.md"
        if not path.exists():
            return f"You are a Cybersecurity Mentor."
        return path.read_text().strip()
        
    @staticmethod
    def build(template_name: str, context: str = "", **kwargs) -> str:
        """
        Loads a template and formats it with **kwargs.
        Optionally prepends a JSON context block if provided.
        """
        template = PromptBuilder._load_template(template_name)
        
        # Format the template with provided kwargs (if any)
        try:
            rendered = template.format(**kwargs)
        except KeyError as e:
            logger.warning("Prompt template '%s' missing variable: %s", template_name, e)
            rendered = template
            
        if context:
            return f"User Context:\n```json\n{context}\n```\n\n{rendered}"
        
        return rendered
