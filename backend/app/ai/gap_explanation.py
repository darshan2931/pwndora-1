import json
import logging
from typing import Any, Dict, List, Optional

from app.ai.orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

GAP_EXPLANATION_SYSTEM = """You are a cybersecurity career advisor. You analyze skill gaps for a specific role and provide actionable, encouraging guidance.

IMPORTANT: Your response must be valid JSON. Do NOT include markdown formatting, code blocks, or any text outside the JSON object.

Return exactly this JSON structure:
{
  "summary": "2-3 sentence overview of the user's readiness for this role",
  "strengths": ["top 3 strengths or covered skills"],
  "critical_gaps": ["top 3 skills that need most attention"],
  "action_plan": ["3-5 specific next steps in order of priority"],
  "estimated_timeline": "rough estimate of time to reach readiness",
  "encouragement": "1 sentence of positive reinforcement"
}

Keep each string under 100 characters. Be specific about skills and numbers."""


class GapExplanationService:
    def __init__(self, orchestrator: Optional[AIOrchestrator] = None):
        self._orchestrator = orchestrator

    def generate_explanation(
        self,
        role_name: str,
        readiness_score: float,
        skill_gaps: List[Dict[str, Any]],
        next_skill: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not self._orchestrator:
            return None

        covered = [g["skill_name"] for g in skill_gaps if g["gap_status"] == "covered"]
        critical = [g["skill_name"] for g in skill_gaps if g["gap_status"] in ("critical", "missing")][:3]
        partial = [g["skill_name"] for g in skill_gaps if g["gap_status"] == "partial"][:3]

        task_prompt = f"""Analyze this role gap assessment for {role_name}:

Readiness: {readiness_score:.0%}

Covered skills ({len(covered)}): {', '.join(covered) if covered else 'None yet'}

Critical gaps: {', '.join(critical) if critical else 'None'}

Partial skills: {', '.join(partial) if covered else 'None'}

Next recommended skill: {next_skill['skill_name'] if next_skill else 'None'} (confidence: {next_skill['confidence']:.0% if next_skill else 'N/A'})

Provide your analysis as JSON only. No markdown, no code blocks."""

        try:
            result = self._orchestrator.execute_task(
                task=task_prompt,
                system_prompt=GAP_EXPLANATION_SYSTEM,
                temperature=0.4,
                max_tokens=500,
            )

            if isinstance(result, str):
                result = self._parse_explanation(result)

            if result and isinstance(result, dict) and "summary" in result:
                return result

            return self._fallback_explanation(role_name, readiness_score, skill_gaps)

        except Exception as e:
            logger.warning("AI explanation failed, using fallback: %s", e)
            return self._fallback_explanation(role_name, readiness_score, skill_gaps)

    def _parse_explanation(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1])

            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            return None

    def _fallback_explanation(
        self,
        role_name: str,
        readiness_score: float,
        skill_gaps: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        covered = [g["skill_name"] for g in skill_gaps if g["gap_status"] == "covered"]
        critical = [g["skill_name"] for g in skill_gaps if g["gap_status"] in ("critical", "missing")][:3]

        if readiness_score >= 0.85:
            summary = f"You're well-prepared for {role_name} with {readiness_score:.0%} readiness."
            encouragement = "You're almost ready to pursue this role professionally!"
        elif readiness_score >= 0.60:
            summary = f"You have a solid foundation for {role_name} at {readiness_score:.0%} readiness."
            encouragement = "Keep building — you're making strong progress."
        elif readiness_score >= 0.30:
            summary = f"You're developing toward {role_name} with {readiness_score:.0%} readiness."
            encouragement = "Every skill you learn brings you closer to this goal."
        else:
            summary = f"You're at {readiness_score:.0%} readiness for {role_name}. There's a path forward."
            encouragement = "Starting from scratch is common — focus on one skill at a time."

        action_plan = []
        if critical:
            action_plan.append(f"Focus first on: {', '.join(critical)}")
        action_plan.append("Complete assessments to build evidence of skills")
        action_plan.append("Work on projects that demonstrate practical ability")

        return {
            "summary": summary,
            "strengths": covered[:3] if covered else ["Foundational knowledge"],
            "critical_gaps": critical if critical else ["None identified"],
            "action_plan": action_plan,
            "estimated_timeline": f"{max(4, len(critical) * 8)}-16 weeks with consistent study",
            "encouragement": encouragement,
        }
