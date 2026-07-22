from typing import Optional, Any
from .orchestrator import AIOrchestrator
from .response_validator import ResponseParser

class AIService:
    """High-level AI service exposed to the rest of the application."""
    
    def __init__(self, provider_name: str = "gemini"):
        self.orchestrator = AIOrchestrator(provider_name)

    def is_configured(self) -> bool:
        return self.orchestrator.is_available()

    async def extract_skills_from_resume(self, resume_text: str) -> dict:
        """Parses a resume to extract skills, certs, and projects."""
        prompt = f"Please extract skills from the following resume:\n\n{resume_text}"
        
        raw_json = await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="resume",
            json_mode=True
        )
        return ResponseParser.parse_resume_skills(raw_json)

    async def mentor_chat(self, question: str, context: str = "", session_id: str = "default", history: list[dict] = None) -> str:
        """Processes a mentor chat request."""
        chat_history = list(history or [])
        chat_history.append({"role": "user", "content": question})

        return await self.orchestrator.chat_session(
            history=chat_history,
            template_name="mentor",
            raw_context=context or None
        )

    async def explain_roadmap(self, roadmap_json: str, context_data: dict) -> str:
        """Generates an encouraging explanation of the generated roadmap."""
        prompt = f"Roadmap Details:\n{roadmap_json}\nExplain this roadmap to the user."
        
        return await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="roadmap",
            context_data=context_data,
            json_mode=False
        )

    async def generate_daily_mission(self, context_data: dict) -> dict:
        """Generates a daily learning mission."""
        prompt = "Generate today's learning mission based on my current progress."
        
        raw_json = await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="mission",
            context_data=context_data,
            json_mode=True
        )
        return raw_json

    async def explain_career(self, context_data: dict) -> str:
        """Explains the career path and readiness score."""
        prompt = "Explain my current career readiness and path forward."
        
        return await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="career",
            context_data=context_data,
            json_mode=False
        )

    async def summarize_session(self, history: list[dict], session_id: str) -> dict:
        """Summarizes a mentor session to reduce context window size for future chats."""
        prompt = (
            "Summarize the following conversation. Identify important facts about the user's progress "
            "and extract their next immediate goal.\n\n"
            f"History:\n{history}"
        )
        
        raw_json = await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="summarize",
            json_mode=True
        )
        return raw_json

    async def run_ocr(self, file_path: str) -> str:
        """Extract text from file using OCR if the primary provider supports it."""
        if self.orchestrator.provider and hasattr(self.orchestrator.provider, "run_ocr"):
            try:
                return await self.orchestrator.provider.run_ocr(file_path)
            except NotImplementedError:
                pass
        return ""

    async def review_resume(self, resume_text: str, career_goal: str) -> str:
        """Reviews a resume against a career goal and provides feedback."""
        prompt = f"Please review the following resume details:\n\n{resume_text}"
        
        return await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="resume_reviewer",
            career_goal=career_goal,
            json_mode=False
        )

    async def generate_proactive_greeting(self, context_str: str) -> str:
        """Generates a proactive greeting based on user context."""
        prompt = "Generate a brief, encouraging greeting for the user."

        return await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="mentor",
            raw_context=context_str,
            json_mode=False
        )

    def clear_session(self, session_id: str) -> None:
        """Clears cached chat session data. Currently a no-op as sessions are managed in DB."""

    async def generate_mentor_response_v2(
        self,
        question: str,
        context: dict,
        mode: str,
        mode_description: str,
        session_id: str = "default",
    ) -> str:
        """Phase 7: Generate an evidence-based mentor response using structured context."""
        import json
        context_block = f"```json\n{json.dumps(context, indent=2, default=str)}\n```"
        prompt = (
            f"Mentor mode: {mode}\n"
            f"Mode description: {mode_description}\n\n"
            f"User question: {question}"
        )

        return await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="mentor_v2",
            raw_context=context_block,
            json_mode=False,
        )

    async def generate_with_template(
        self,
        template_name: str,
        context: dict,
        question: str,
    ) -> str:
        """Phase 7: Generate a response using a specific prompt template and context."""
        import json
        context_block = f"```json\n{json.dumps(context, indent=2, default=str)}\n```"
        return await self.orchestrator.execute_task(
            task_prompt=question,
            template_name=template_name,
            raw_context=context_block,
            json_mode=False,
        )

    async def explain_opportunity(self, context: dict) -> str:
        """Phase 8: Explain an opportunity match to the user with actionable advice."""
        import json
        context_block = f"```json\n{json.dumps(context, indent=2, default=str)}\n```"
        prompt = (
            f"Explain the opportunity match for: {context.get('opportunity_title', 'Unknown')} "
            f"(Score: {context.get('match_score', 0)}/100, Category: {context.get('category', 'unknown')})"
        )
        return await self.orchestrator.execute_task(
            task_prompt=prompt,
            template_name="opportunity_explanation",
            raw_context=context_block,
            json_mode=False,
        )

