import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.gap_analysis_service import GapAnalysisService
from services.role_adapter import RoleAdapter
from repositories.repositories import SkillEvidenceRepository, CareerRoleAnalysisRepository
from knowledge.loader import KnowledgeLoader

logger = logging.getLogger(__name__)


class RoleGapAnalysisService:
    def __init__(
        self,
        gap_analysis_service: Optional[GapAnalysisService] = None,
        role_adapter: Optional[RoleAdapter] = None,
        knowledge_loader: Optional[KnowledgeLoader] = None,
    ):
        self._gap_service = gap_analysis_service or GapAnalysisService()
        self._role_adapter = role_adapter or RoleAdapter()
        self._knowledge_loader = knowledge_loader or KnowledgeLoader()
        self._skill_evidence_repo = SkillEvidenceRepository()
        self._role_analysis_repo = CareerRoleAnalysisRepository()

    def analyze_role_gap(self, user_id: str, role_id: str) -> Dict[str, Any]:
        role_enriched = self._role_adapter.get_role_enriched(role_id)
        if not role_enriched:
            return {"error": f"Role '{role_id}' not found"}

        skill_confidences = self._load_user_skill_confidences(user_id)

        readiness = self._gap_service.calculate_readiness(role_id, skill_confidences)
        overall_readiness = readiness["overall_readiness"]

        skill_gaps = self._build_skill_gaps(
            role_id, skill_confidences, readiness
        )

        priority_breakdown = self._build_priority_breakdown(skill_gaps)

        next_skill = self._gap_service.find_next_skill(role_id, skill_confidences)

        learning_path = self._gap_service.get_learning_path_for_role(role_id)

        covered_count = sum(1 for g in skill_gaps if g["gap_status"] == "covered")
        partial_count = sum(1 for g in skill_gaps if g["gap_status"] in ("partial", "minimal"))
        missing_count = sum(1 for g in skill_gaps if g["gap_status"] in ("missing", "critical"))
        total_skills = len(skill_gaps)

        result = {
            "role_id": role_id,
            "role_name": role_enriched["role_name"],
            "role_description": role_enriched["description"],
            "readiness_score": overall_readiness,
            "readiness_level": self._gap_service.determine_readiness_level(overall_readiness),
            "total_skills": total_skills,
            "covered_count": covered_count,
            "partial_count": partial_count,
            "missing_count": missing_count,
            "skill_gaps": skill_gaps,
            "priority_breakdown": priority_breakdown,
            "recommended_next_skill": next_skill,
            "learning_path": learning_path,
            "ai_explanation": None,
            "analyzed_at": datetime.utcnow().isoformat(),
        }

        return result

    def _load_user_skill_confidences(self, user_id: str) -> Dict[str, float]:
        evidences = self._skill_evidence_repo.get_by_user_id(user_id)
        if not evidences:
            return {}

        confidences = {}
        for ev in evidences:
            skill_id = ev.skill_id if hasattr(ev, "skill_id") else ev.skill_name
            confidence = ev.confidence / 100.0 if hasattr(ev, "confidence") and ev.confidence else 0.0
            confidences[skill_id] = confidence

        return confidences

    def _build_skill_gaps(
        self,
        role_id: str,
        skill_confidences: Dict[str, float],
        readiness: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        role_enriched = self._role_adapter.get_role_enriched(role_id)
        if not role_enriched:
            return []

        skill_gaps = []

        req_skills = readiness.get("required_skills", {})
        for skill_id, req_info in req_skills.items():
            confidence = req_info.get("confidence", 0.0)
            min_conf = req_info.get("minimum_confidence", 0.5)
            gap = self._gap_service.calculate_skill_gap(
                role_id, skill_id, confidence, is_required=True
            )
            gap["importance"] = req_info.get("importance", "important")
            gap["importance_score"] = req_info.get("importance_score", 0.5)
            gap["minimum_confidence"] = min_conf

            gap["priority_score"] = self._gap_service.calculate_priority_score(gap)
            gap["priority_level"] = self._determine_priority_level(gap["priority_score"])

            unblocked = self._gap_service._get_unblocked_skills(skill_id)
            gap["unblocked_skills"] = unblocked

            if gap["gap_status"] in ("covered",):
                gap["recommendation_reason"] = f"Already meets minimum ({confidence:.0%} >= {min_conf:.0%})"
            elif gap["gap_status"] == "minimal":
                gap["recommendation_reason"] = f"Almost there — {gap['gap_size']:.0%} gap to close"
            elif not gap["blocked_by"]:
                gap["recommendation_reason"] = self._gap_service._build_recommendation_reason(gap)
            else:
                gap["recommendation_reason"] = f"Blocked by: {', '.join(gap['blocked_by'])}"

            skill_gaps.append(gap)

        opt_skills = readiness.get("optional_skills", {})
        for skill_id, opt_info in opt_skills.items():
            confidence = opt_info.get("confidence", 0.0)
            importance_score = opt_info.get("importance_score", 0.5)
            min_conf = importance_score * 0.6

            gap = self._gap_service.calculate_skill_gap(
                role_id, skill_id, confidence, is_required=False
            )
            gap["importance"] = opt_info.get("importance", "beneficial")
            gap["importance_score"] = importance_score
            gap["minimum_confidence"] = min_conf

            gap["priority_score"] = self._gap_service.calculate_priority_score(gap)
            gap["priority_level"] = self._determine_priority_level(gap["priority_score"])

            unblocked = self._gap_service._get_unblocked_skills(skill_id)
            gap["unblocked_skills"] = unblocked

            if gap["gap_status"] == "covered":
                gap["recommendation_reason"] = f"Bonus — {confidence:.0%} confidence"
            else:
                gap["recommendation_reason"] = f"Optional skill — {gap['gap_size']:.0%} gap"

            skill_gaps.append(gap)

        skill_gaps.sort(key=lambda g: g["priority_score"], reverse=True)

        return skill_gaps

    def _determine_priority_level(self, score: float) -> str:
        if score >= 0.7:
            return "highest"
        elif score >= 0.5:
            return "high"
        elif score >= 0.3:
            return "medium"
        return "low"

    def _build_priority_breakdown(self, skill_gaps: List[Dict[str, Any]]) -> Dict[str, List]:
        breakdown = {"highest": [], "high": [], "medium": [], "low": []}
        for gap in skill_gaps:
            level = gap.get("priority_level", "low")
            if level in breakdown:
                breakdown[level].append(gap)
        return breakdown

    def save_analysis(self, user_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        existing = self._role_analysis_repo.get_by_user_and_role(
            user_id, analysis["role_id"]
        )

        skill_gaps_json = json.dumps(analysis["skill_gaps"])
        priority_json = json.dumps(analysis["priority_breakdown"])
        learning_json = json.dumps(analysis["learning_path"])

        readiness_int = int(analysis["readiness_score"] * 100)

        data = {
            "role_id": analysis["role_id"],
            "role_name": analysis["role_name"],
            "readiness_score": readiness_int,
            "readiness_level": analysis["readiness_level"],
            "total_skills": analysis["total_skills"],
            "covered_count": analysis["covered_count"],
            "partial_count": analysis["partial_count"],
            "missing_count": analysis["missing_count"],
            "skill_gaps": skill_gaps_json,
            "priority_breakdown": priority_json,
            "recommended_next_skill": analysis.get("recommended_next_skill"),
            "learning_path": learning_json,
            "ai_explanation": analysis.get("ai_explanation"),
            "analyzed_at": datetime.utcnow(),
        }

        if existing:
            return self._role_analysis_repo.update(existing.id, **data)
        return self._role_analysis_repo.create(user_id, **data)

    def get_saved_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        analysis = self._role_analysis_repo.get_by_user_id(user_id)
        if not analysis:
            return None

        skill_gaps = analysis.skill_gaps if isinstance(analysis.skill_gaps, list) else json.loads(analysis.skill_gaps or "[]")
        priority = analysis.priority_breakdown if isinstance(analysis.priority_breakdown, dict) else json.loads(analysis.priority_breakdown or "{}")
        learning = analysis.learning_path if isinstance(analysis.learning_path, list) else json.loads(analysis.learning_path or "[]")

        return {
            "role_id": analysis.role_id,
            "role_name": analysis.role_name,
            "role_description": "",
            "readiness_score": analysis.readiness_score / 100.0 if analysis.readiness_score else 0.0,
            "readiness_level": analysis.readiness_level,
            "total_skills": analysis.total_skills,
            "covered_count": analysis.covered_count,
            "partial_count": analysis.partial_count,
            "missing_count": analysis.missing_count,
            "skill_gaps": skill_gaps,
            "priority_breakdown": priority,
            "recommended_next_skill": analysis.recommended_next_skill,
            "learning_path": learning,
            "ai_explanation": analysis.ai_explanation,
            "analyzed_at": analysis.analyzed_at.isoformat() if analysis.analyzed_at else None,
        }

    def get_next_skill(self, user_id: str) -> Optional[Dict[str, Any]]:
        analysis = self.get_saved_analysis(user_id)
        if not analysis:
            return None
        return analysis.get("recommended_next_skill")
