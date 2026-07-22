import json
import logging
from typing import Any, Dict, List, Optional

from app.ai.orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

ROADMAP_EXPLANATION_SYSTEM = """You are a cybersecurity career advisor. You explain personalized learning roadmaps to users.

IMPORTANT: Your response must be valid JSON. Do NOT include markdown formatting, code blocks, or any text outside the JSON object.

Return exactly this JSON structure:
{
  "overview": "2-3 sentence overview of this roadmap and why it's structured this way",
  "phase_highlights": [{"phase": "phase name", "highlight": "key focus area in 1 sentence"}],
  "first_steps": ["2-3 specific things to start with right now"],
  "milestones": ["2-3 key milestones to look forward to"],
  "personalization_notes": "1-2 sentences about how this roadmap was personalized based on their skills"
}

Keep each string under 120 characters. Be encouraging and specific."""


class RoadmapExplanationService:
    def __init__(self, orchestrator: Optional[AIOrchestrator] = None):
        self._orchestrator = orchestrator

    def generate_explanation(
        self,
        role_name: str,
        readiness_score: float,
        nodes: List[Dict[str, Any]],
        phases: List[Dict[str, Any]],
        skill_confidences: Dict[str, float],
    ) -> Optional[Dict[str, Any]]:
        if not self._orchestrator:
            return None

        skill_nodes = [n for n in nodes if n.get("type") == "skill"]
        project_nodes = [n for n in nodes if n.get("type") == "project"]
        cert_nodes = [n for n in nodes if n.get("type") == "certification"]

        covered_skills = [s for s, c in skill_confidences.items() if c >= 0.6]
        learning_skills = [n["title"] for n in skill_nodes[:5]]

        phase_names = [p.get("name", "") for p in phases[:5]]

        task_prompt = f"""Explain this personalized roadmap for {role_name}:

Readiness: {readiness_score:.0%}
Total steps: {len(nodes)} ({len(skill_nodes)} skills, {len(project_nodes)} projects, {len(cert_nodes)} certifications)
Phases: {', '.join(phase_names)}

Already covered: {', '.join(covered_skills[:5]) if covered_skills else 'None yet'}
First skills to learn: {', '.join(learning_skills)}

Provide your explanation as JSON only. No markdown, no code blocks."""

        try:
            result = self._orchestrator.execute_task(
                task=task_prompt,
                system_prompt=ROADMAP_EXPLANATION_SYSTEM,
                temperature=0.4,
                max_tokens=600,
            )

            if isinstance(result, str):
                result = self._parse_explanation(result)

            if result and isinstance(result, dict) and "overview" in result:
                return result

            return self._fallback_explanation(role_name, readiness_score, nodes, phases, skill_confidences)

        except Exception as e:
            logger.warning("AI roadmap explanation failed, using fallback: %s", e)
            return self._fallback_explanation(role_name, readiness_score, nodes, phases, skill_confidences)

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
        nodes: List[Dict[str, Any]],
        phases: List[Dict[str, Any]],
        skill_confidences: Dict[str, float],
    ) -> Dict[str, Any]:
        skill_nodes = [n for n in nodes if n.get("type") == "skill"]
        covered = [s for s, c in skill_confidences.items() if c >= 0.6]

        if readiness_score >= 0.7:
            overview = f"You're well on your way to {role_name} with {readiness_score:.0%} readiness. This roadmap focuses on filling remaining gaps."
        elif readiness_score >= 0.4:
            overview = f"You have a solid foundation for {role_name} at {readiness_score:.0%} readiness. This roadmap builds on your existing skills."
        else:
            overview = f"This roadmap takes you from {readiness_score:.0%} readiness to job-ready for {role_name}."

        first_steps = []
        for n in skill_nodes[:3]:
            first_steps.append(f"Start with {n['title']} ({n.get('estimatedHours', 10)}h)")

        milestones = []
        if len(phases) > 2:
            milestones.append(f"Complete {phases[1].get('name', 'Phase 2')}")
        milestones.append(f"Finish {len([n for n in nodes if n.get('type') == 'project'])} portfolio projects")

        return {
            "overview": overview,
            "phase_highlights": [
                {"phase": p.get("name", ""), "highlight": f"Focus on {p.get('skillCount', 0)} core skills"}
                for p in phases[:4]
            ],
            "first_steps": first_steps if first_steps else ["Begin with foundational skills"],
            "milestones": milestones,
            "personalization_notes": f"Personalized based on your {len(covered)} existing skills and learning pace.",
        }


roadmap_explanation_service = RoadmapExplanationService()
