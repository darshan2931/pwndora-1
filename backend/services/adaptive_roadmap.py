import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.repositories import (
    RoadmapRepository,
    RoadmapVersionRepository,
    SkillEvidenceRepository,
    AssessmentRepository,
)
from services.personalized_roadmap_service import PersonalizedRoadmapService
from services.role_gap_analysis_service import RoleGapAnalysisService

logger = logging.getLogger(__name__)


class AdaptiveRoadmapService:
    def __init__(
        self,
        roadmap_repo: Optional[RoadmapRepository] = None,
        version_repo: Optional[RoadmapVersionRepository] = None,
        skill_evidence_repo: Optional[SkillEvidenceRepository] = None,
        assessment_repo: Optional[AssessmentRepository] = None,
        roadmap_service: Optional[PersonalizedRoadmapService] = None,
        role_gap_service: Optional[RoleGapAnalysisService] = None,
    ):
        self._roadmap_repo = roadmap_repo or RoadmapRepository()
        self._version_repo = version_repo or RoadmapVersionRepository()
        self._skill_evidence_repo = skill_evidence_repo or SkillEvidenceRepository()
        self._assessment_repo = assessment_repo or AssessmentRepository()
        self._roadmap_service = roadmap_service or PersonalizedRoadmapService()
        self._role_gap = role_gap_service or RoleGapAnalysisService()

    def should_regenerate(
        self,
        user_id: str,
        event_type: str,
        confidence_delta: float,
        impacted_skills: List[str],
    ) -> Dict[str, Any]:
        current_roadmap = self._roadmap_repo.get_latest_by_user_and_assessment(user_id, "")
        if not current_roadmap:
            roadmaps = self._roadmap_repo.get_by_user_id(user_id, limit=1)
            current_roadmap = roadmaps[0] if roadmaps else None

        if not current_roadmap:
            return {"should_regenerate": False, "reason": "no_roadmap"}

        changes_significant = confidence_delta >= 10 or event_type in (
            "roadmap_project_completed", "roadmap_certification_completed", "certification_added"
        )

        high_impact_skills = [s for s in impacted_skills[:3]]

        return {
            "should_regenerate": changes_significant,
            "reason": "skill_milestone" if changes_significant else "minor_update",
            "current_roadmap_id": str(current_roadmap.id),
            "impacted_skills": high_impact_skills,
        }

    def update_roadmap_status(
        self,
        user_id: str,
        updated_skills: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        roadmaps = self._roadmap_repo.get_by_user_id(user_id, limit=1)
        if not roadmaps:
            return {"updated": False, "reason": "no_roadmap"}

        roadmap = roadmaps[0]
        nodes = roadmap.steps or []
        if not nodes:
            return {"updated": False, "reason": "empty_roadmap"}

        updated_count = 0
        for node in nodes:
            node_skills = node.get("skills", [])
            for updated in updated_skills:
                skill_id = updated.get("skill_id", "")
                if skill_id in node_skills:
                    if node.get("status") == "locked":
                        node["status"] = "available"
                        updated_count += 1
                    elif node.get("status") == "available":
                        new_conf = updated.get("new_confidence", 0)
                        if new_conf >= 80:
                            node["status"] = "completed"
                            node["completedAt"] = datetime.utcnow().isoformat()
                            updated_count += 1

        if updated_count > 0:
            self._roadmap_repo.update_steps(str(roadmap.id), nodes)

        return {
            "updated": updated_count > 0,
            "nodes_updated": updated_count,
            "roadmap_id": str(roadmap.id),
        }

    def create_version_snapshot(
        self,
        user_id: str,
        assessment_id: str,
        event_id: str = None,
        reason: str = "evidence_update",
    ) -> Dict[str, Any]:
        next_version = self._version_repo.get_next_version_number(user_id)

        latest_roadmap = self._roadmap_repo.get_latest_by_user_and_assessment(user_id, assessment_id)
        previous_version_id = None
        readiness_score = 0
        nodes_snapshot = []
        phases_snapshot = []
        total_hours = 0
        estimated_weeks = 0

        if latest_roadmap:
            previous_version_id = str(latest_roadmap.id)
            readiness_score = latest_roadmap.readiness_score_at_creation or 0
            nodes_snapshot = latest_roadmap.steps or []
            phases_snapshot = latest_roadmap.phases or []
            total_hours = latest_roadmap.total_hours or 0
            estimated_weeks = latest_roadmap.estimated_weeks or 0

        version = self._version_repo.create(
            user_id=user_id,
            assessment_id=assessment_id,
            version_number=next_version,
            generation_reason=reason,
            triggered_by_event_id=event_id,
            previous_version_id=previous_version_id,
            readiness_score_at_creation=readiness_score,
            nodes_snapshot=nodes_snapshot,
            phases_snapshot=phases_snapshot,
            total_hours=total_hours,
            estimated_weeks=estimated_weeks,
        )

        return {
            "version_id": str(version.id),
            "version_number": next_version,
            "reason": reason,
        }

    def get_version_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        versions = self._version_repo.get_by_user_id(user_id, limit=limit)
        return [
            {
                "id": str(v.id),
                "version_number": v.version_number,
                "generation_reason": v.generation_reason,
                "readiness_score_at_creation": v.readiness_score_at_creation,
                "nodes_count": len(v.nodes_snapshot or []),
                "total_hours": v.total_hours,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in versions
        ]
