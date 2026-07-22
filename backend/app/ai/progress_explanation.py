import logging
from typing import Any, Dict, List, Optional

from app.ai.orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

PROGRESS_EXPLANATION_SYSTEM = """You are a cybersecurity career advisor. You explain how user actions impact their career readiness.

IMPORTANT: Your response must be valid JSON. Do NOT include markdown formatting, code blocks, or any text outside the JSON object.

Return exactly this JSON structure:
{
  "summary": "1-2 sentence summary of what changed and why it matters",
  "skill_impact": "How the affected skills changed in confidence",
  "readiness_impact": "How this affects overall career readiness",
  "next_steps": ["2-3 suggested next actions"],
  "encouragement": "1 sentence of encouragement"
}

Keep each string under 150 characters. Be specific and encouraging."""


class ProgressExplanationService:
    def __init__(self, orchestrator: Optional[AIOrchestrator] = None):
        self._orchestrator = orchestrator

    def explain_change(
        self,
        change_type: str,
        skill_name: str,
        old_confidence: float,
        new_confidence: float,
        old_readiness: float,
        new_readiness: float,
        impacted_skills: List[str] = None,
        impacted_roles: List[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if not self._orchestrator or not self._orchestrator.is_available():
            return self._fallback_explanation(
                change_type, skill_name, old_confidence, new_confidence,
                old_readiness, new_readiness,
            )

        task_prompt = f"""Explain this career progress update:

Action: {change_type.replace('_', ' ').title()}
Skill: {skill_name}
Confidence: {old_confidence:.0f}% → {new_confidence:.0f}%
Readiness: {old_readiness:.0f}% → {new_readiness:.0f}%
Impacted skills: {', '.join(impacted_skills[:5]) if impacted_skills else 'None'}
Impacted roles: {', '.join(impacted_roles[:3]) if impacted_roles else 'None'}

Provide your explanation as JSON only. No markdown, no code blocks."""

        try:
            result = self._orchestrator.execute_task(
                task=task_prompt,
                system_prompt=PROGRESS_EXPLANATION_SYSTEM,
                temperature=0.4,
                max_tokens=500,
            )
            if isinstance(result, str):
                result = self._parse_json(result)
            if result and isinstance(result, dict) and "summary" in result:
                return result
        except Exception as e:
            logger.warning("AI progress explanation failed: %s", e)

        return self._fallback_explanation(
            change_type, skill_name, old_confidence, new_confidence,
            old_readiness, new_readiness,
        )

    def explain_readiness_change(
        self,
        old_readiness: float,
        new_readiness: float,
        changes: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if not self._orchestrator or not self._orchestrator.is_available():
            return self._fallback_readiness_explanation(old_readiness, new_readiness, changes)

        changes_summary = []
        for c in changes[:5]:
            changes_summary.append(f"{c.get('skill_name', '?')}: {c.get('old_confidence', 0):.0f}%→{c.get('new_confidence', 0):.0f}%")

        task_prompt = f"""Explain this overall readiness change:

Readiness: {old_readiness:.0f}% → {new_readiness:.0f}% (delta: {new_readiness - old_readiness:+.1f}%)
Key changes: {'; '.join(changes_summary)}

Provide your explanation as JSON only. No markdown, no code blocks."""

        try:
            result = self._orchestrator.execute_task(
                task=task_prompt,
                system_prompt=PROGRESS_EXPLANATION_SYSTEM,
                temperature=0.4,
                max_tokens=500,
            )
            if isinstance(result, str):
                result = self._parse_json(result)
            if result and isinstance(result, dict) and "summary" in result:
                return result
        except Exception as e:
            logger.warning("AI readiness explanation failed: %s", e)

        return self._fallback_readiness_explanation(old_readiness, new_readiness, changes)

    def _fallback_explanation(
        self,
        change_type: str,
        skill_name: str,
        old_confidence: float,
        new_confidence: float,
        old_readiness: float,
        new_readiness: float,
    ) -> Dict[str, Any]:
        delta = new_confidence - old_confidence
        readiness_delta = new_readiness - old_readiness

        if delta > 0:
            summary = f"Completed {change_type.replace('_', ' ')} for {skill_name}. Confidence increased by {delta:.0f}%."
            skill_impact = f"{skill_name} confidence improved from {old_confidence:.0f}% to {new_confidence:.0f}%."
        else:
            summary = f"Processed {change_type.replace('_', ' ')} for {skill_name}. No confidence change."
            skill_impact = f"{skill_name} confidence remains at {new_confidence:.0f}%."

        if readiness_delta > 0:
            readiness_impact = f"Overall readiness improved by {readiness_delta:.1f}% ({old_readiness:.0f}% → {new_readiness:.0f}%)."
        elif readiness_delta < 0:
            readiness_impact = f"Overall readiness changed from {old_readiness:.0f}% to {new_readiness:.0f}%."
        else:
            readiness_impact = f"Overall readiness remains at {new_readiness:.0f}%."

        return {
            "summary": summary,
            "skill_impact": skill_impact,
            "readiness_impact": readiness_impact,
            "next_steps": ["Continue learning to build more evidence", "Review your roadmap for next steps"],
            "encouragement": "Every step forward counts toward your career goal!",
        }

    def _fallback_readiness_explanation(
        self,
        old_readiness: float,
        new_readiness: float,
        changes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        delta = new_readiness - old_readiness
        if delta > 0:
            summary = f"Your readiness score improved by {delta:.1f}% following {len(changes)} skill updates."
            encouragement = f"Great progress! You're now at {new_readiness:.0f}% readiness."
        elif delta < 0:
            summary = f"Your readiness score changed from {old_readiness:.0f}% to {new_readiness:.0f}%."
            encouragement = "Keep pushing forward — every skill counts!"
        else:
            summary = f"Your readiness score remains at {new_readiness:.0f}%."
            encouragement = "Stay consistent and the progress will come."

        return {
            "summary": summary,
            "skill_impact": f"{len(changes)} skills were updated.",
            "readiness_impact": f"Readiness: {old_readiness:.0f}% → {new_readiness:.0f}%.",
            "next_steps": ["Review your skill gaps", "Focus on high-priority missing skills"],
            "encouragement": encouragement,
        }

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        import json
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return None
