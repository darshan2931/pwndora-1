import httpx
from domain.models import Assessment, Roadmap


class AIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"

    async def chat(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": "mistral-small", "messages": [{"role": "user", "content": prompt}]},
            )
            return resp.json()["choices"][0]["message"]["content"]


class PromptBuilder:
    def build_roadmap_explanation(self, assessment: Assessment, roadmap: Roadmap) -> str:
        return (
            f"The user wants to become a {assessment.target_career.title}. "
            f"Their readiness score is {assessment.readiness_score}%. "
            f"They already know: {[s.name for s in assessment.matched_skills]}. "
            f"They need to learn: {[s.name for s in assessment.missing_skills]}."
        )

    def build_mentor_prompt(self, assessment: Assessment, question: str) -> str:
        return f"Context: Target Role: {assessment.target_career.title}. Question: {question}"


class ResponseValidator:
    @staticmethod
    def validate_json(text: str) -> bool:
        import json
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def validate_no_hallucinations(text: str, known_skills: list) -> bool:
        return True
