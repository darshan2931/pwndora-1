import json
import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StructuredMentorResponse:
    def __init__(
        self,
        answer: str,
        confidence: str = "medium",
        sources: List[Dict[str, str]] = None,
        recommended_actions: List[Dict[str, str]] = None,
        warnings: List[str] = None,
        mode: str = "general",
    ):
        self.answer = answer
        self.confidence = confidence
        self.sources = sources or []
        self.recommended_actions = recommended_actions or []
        self.warnings = warnings or []
        self.mode = mode

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "sources": self.sources,
            "recommended_actions": self.recommended_actions,
            "warnings": self.warnings,
            "mode": self.mode,
        }

    def to_response(self) -> dict:
        return {"success": True, **self.to_dict()}


class StructuredResponseParser:
    @staticmethod
    def parse_ai_response(raw: str, mode: str = "general") -> StructuredMentorResponse:
        if not raw:
            return StructuredMentorResponse(
                answer="I couldn't generate a response. Please try again.",
                confidence="low",
                mode=mode,
            )

        parsed = StructuredResponseParser._try_parse_json(raw)
        if parsed and isinstance(parsed, dict) and "answer" in parsed:
            return StructuredMentorResponse(
                answer=str(parsed.get("answer", raw)),
                confidence=str(parsed.get("confidence", "medium")),
                sources=StructuredResponseParser._normalize_sources(parsed.get("sources", [])),
                recommended_actions=StructuredResponseParser._normalize_actions(parsed.get("recommended_actions", [])),
                warnings=[str(w) for w in parsed.get("warnings", [])],
                mode=mode,
            )

        return StructuredMentorResponse(
            answer=raw,
            confidence="medium",
            mode=mode,
        )

    @staticmethod
    def _try_parse_json(text: str) -> Optional[dict]:
        try:
            cleaned = text.strip()
            fence = re.compile(r'^```(?:json|JSON)?\s*\n?', re.MULTILINE)
            cleaned = fence.sub('', cleaned)
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def _normalize_sources(sources: Any) -> List[Dict[str, str]]:
        if not isinstance(sources, list):
            return []
        result = []
        for s in sources:
            if isinstance(s, dict):
                result.append({
                    "type": str(s.get("type", "unknown")),
                    "skill": str(s.get("skill", "")),
                    "detail": str(s.get("detail", "")),
                })
            elif isinstance(s, str):
                result.append({"type": "reference", "skill": "", "detail": s})
        return result

    @staticmethod
    def _normalize_actions(actions: Any) -> List[Dict[str, str]]:
        if not isinstance(actions, list):
            return []
        result = []
        for a in actions:
            if isinstance(a, dict):
                result.append({
                    "title": str(a.get("title", "")),
                    "reason": str(a.get("reason", "")),
                })
            elif isinstance(a, str):
                result.append({"title": a, "reason": ""})
        return result


class SourceBuilder:
    @staticmethod
    def build_from_context(context: dict, skill_name: str = None) -> List[Dict[str, str]]:
        sources = []
        
        evidence = context.get("evidence_summary", {})
        if evidence.get("resume"):
            sources.append({"type": "resume", "skill": skill_name or "", "detail": "Resume evidence detected"})
        if evidence.get("github_repos", 0) > 0:
            sources.append({
                "type": "github",
                "skill": skill_name or "",
                "detail": f"{evidence['github_repos']} GitHub repositories analyzed"
            })
        
        for s in context.get("strengths", []):
            if skill_name and s.get("skill", "").lower() == skill_name.lower():
                sources.append({
                    "type": "skill_evidence",
                    "skill": s["skill"],
                    "detail": f"Confidence: {s.get('confidence', 0):.0%}"
                })
                break
        
        role = context.get("readiness", {})
        if role.get("score", 0) > 0:
            sources.append({
                "type": "role_analysis",
                "skill": skill_name or "",
                "detail": f"Readiness: {role['score']}%"
            })
        
        return sources

    @staticmethod
    def build_from_evidence(skill_name: str, evidence_list: list) -> List[Dict[str, str]]:
        sources = []
        for ev in evidence_list:
            sources.append({
                "type": ev.get("source", "unknown"),
                "skill": skill_name,
                "detail": ev.get("detail", ""),
            })
        return sources
