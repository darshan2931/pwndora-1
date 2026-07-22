import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.repositories import (
    CareerEvidenceEventRepository,
    CareerChangeLogRepository,
    SkillEvidenceRepository,
    UserSkillProfileRepository,
    CareerRoleAnalysisRepository,
    RoadmapRepository,
    RoadmapVersionRepository,
)
from services.evidence_event_processor import EvidenceEventProcessor
from services.impact_analysis import ImpactAnalysis
from services.adaptive_roadmap import AdaptiveRoadmapService
from services.role_gap_analysis_service import RoleGapAnalysisService
from app.ai.progress_explanation import ProgressExplanationService
from knowledge.loader import KnowledgeLoader

logger = logging.getLogger(__name__)


class CareerProgressService:
    def __init__(
        self,
        event_processor: Optional[EvidenceEventProcessor] = None,
        change_log_repo: Optional[CareerChangeLogRepository] = None,
        event_repo: Optional[CareerEvidenceEventRepository] = None,
        skill_evidence_repo: Optional[SkillEvidenceRepository] = None,
        skill_profile_repo: Optional[UserSkillProfileRepository] = None,
        role_analysis_repo: Optional[CareerRoleAnalysisRepository] = None,
        adaptive_roadmap: Optional[AdaptiveRoadmapService] = None,
        impact_analysis: Optional[ImpactAnalysis] = None,
        role_gap_service: Optional[RoleGapAnalysisService] = None,
        explanation_service: Optional[ProgressExplanationService] = None,
        knowledge_loader: Optional[KnowledgeLoader] = None,
    ):
        self._event_processor = event_processor or EvidenceEventProcessor()
        self._change_log_repo = change_log_repo or CareerChangeLogRepository()
        self._event_repo = event_repo or CareerEvidenceEventRepository()
        self._skill_evidence_repo = skill_evidence_repo or SkillEvidenceRepository()
        self._skill_profile_repo = skill_profile_repo or UserSkillProfileRepository()
        self._role_analysis_repo = role_analysis_repo or CareerRoleAnalysisRepository()
        self._adaptive_roadmap = adaptive_roadmap or AdaptiveRoadmapService()
        self._impact = impact_analysis or ImpactAnalysis()
        self._role_gap = role_gap_service or RoleGapAnalysisService()
        self._explanation = explanation_service or ProgressExplanationService()
        self._knowledge = knowledge_loader or KnowledgeLoader()

    def process_event(
        self,
        user_id: str,
        event_type: str,
        event_data: dict = None,
        idempotency_key: str = None,
    ) -> Dict[str, Any]:
        event_result = self._event_processor.create_event(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            idempotency_key=idempotency_key,
        )

        if event_result.get("duplicate"):
            return {
                "success": True,
                "message": "Duplicate event ignored",
                "event_id": event_result["event_id"],
            }

        event_id = event_result["event_id"]

        pre_readiness = self._get_current_readiness(user_id)

        process_result = self._event_processor.process_event(event_id)

        if not process_result.get("success"):
            return process_result

        post_readiness = self._get_current_readiness(user_id)

        changes = self._record_changes(user_id, event_id, event_type, process_result)

        roadmap_decision = self._adaptive_roadmap.should_regenerate(
            user_id, event_type,
            process_result.get("confidence_delta", 0),
            process_result.get("impacted_skills", []),
        )

        roadmap_update = self._adaptive_roadmap.update_roadmap_status(
            user_id, process_result.get("skills_updated", []),
        )

        explanation = self._explanation.explain_change(
            change_type=event_type,
            skill_name=process_result.get("skill_id", process_result.get("certification_name", "")),
            old_confidence=process_result.get("old_confidence", 0),
            new_confidence=process_result.get("new_confidence", 0),
            old_readiness=pre_readiness,
            new_readiness=post_readiness,
            impacted_skills=process_result.get("impacted_skills", []),
            impacted_roles=process_result.get("impacted_roles", []),
        )

        if explanation:
            for change in changes:
                self._change_log_repo.update(change.id, ai_explanation=explanation.get("summary"))

        return {
            "success": True,
            "event_id": event_id,
            "changes": [
                {
                    "change_type": c.change_type,
                    "skill_name": c.skill_name,
                    "old_value": c.old_value,
                    "new_value": c.new_value,
                    "confidence_delta": c.confidence_delta,
                    "readiness_delta": c.readiness_delta,
                    "explanation": c.explanation,
                }
                for c in changes
            ],
            "readiness": {
                "old": pre_readiness,
                "new": post_readiness,
                "delta": post_readiness - pre_readiness,
            },
            "roadmap": {
                "should_regenerate": roadmap_decision.get("should_regenerate", False),
                "nodes_updated": roadmap_update.get("nodes_updated", 0),
            },
            "explanation": explanation,
        }

    def get_timeline(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        changes = self._change_log_repo.get_by_user_id(user_id, limit=limit)
        timeline = []
        for c in changes:
            timeline.append({
                "id": str(c.id),
                "event_id": str(c.event_id),
                "change_type": c.change_type,
                "skill_name": c.skill_name,
                "old_value": c.old_value,
                "new_value": c.new_value,
                "confidence_delta": c.confidence_delta,
                "readiness_delta": c.readiness_delta,
                "explanation": c.explanation,
                "ai_explanation": c.ai_explanation,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            })
        return timeline

    def get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        evidences = self._skill_evidence_repo.get_by_user_id(user_id)

        high = sum(1 for e in evidences if (e.confidence or 0) >= 80)
        medium = sum(1 for e in evidences if 60 <= (e.confidence or 0) < 80)
        low = sum(1 for e in evidences if 40 <= (e.confidence or 0) < 60)
        minimal = sum(1 for e in evidences if (e.confidence or 0) < 40)
        total = len(evidences)
        avg = sum(e.confidence or 0 for e in evidences) / total if total > 0 else 0

        recent_events = self._event_repo.get_by_user_id(user_id, limit=10)
        processed = sum(1 for e in recent_events if e.status == "processed")
        pending = sum(1 for e in recent_events if e.status == "pending")

        role_analysis = self._role_analysis_repo.get_by_user_id(user_id)
        readiness_score = role_analysis.readiness_score if role_analysis else 0
        readiness_level = role_analysis.readiness_level if role_analysis else "not_started"

        versions = self._adaptive_roadmap.get_version_history(user_id, limit=5)

        return {
            "skills": {
                "total": total,
                "high": high,
                "medium": medium,
                "low": low,
                "minimal": minimal,
                "average_confidence": round(avg, 1),
            },
            "readiness": {
                "score": readiness_score,
                "level": readiness_level,
            },
            "events": {
                "recent_total": len(recent_events),
                "processed": processed,
                "pending": pending,
            },
            "roadmap_versions": versions,
        }

    def get_change_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        changes = self._change_log_repo.get_by_user_id(user_id, limit=limit)
        return [
            {
                "id": str(c.id),
                "event_id": str(c.event_id),
                "change_type": c.change_type,
                "skill_name": c.skill_name,
                "old_value": c.old_value,
                "new_value": c.new_value,
                "confidence_delta": c.confidence_delta,
                "readiness_delta": c.readiness_delta,
                "explanation": c.explanation,
                "ai_explanation": c.ai_explanation,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in changes
        ]

    def get_event_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        event = self._event_repo.get_by_id(event_id)
        if not event:
            return None
        changes = self._change_log_repo.get_by_event_id(event_id)
        return {
            "id": str(event.id),
            "event_type": event.event_type,
            "status": event.status,
            "event_data": event.event_data,
            "retry_count": event.retry_count,
            "error_message": event.error_message,
            "processed_at": event.processed_at.isoformat() if event.processed_at else None,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "changes": [
                {
                    "change_type": c.change_type,
                    "skill_name": c.skill_name,
                    "confidence_delta": c.confidence_delta,
                    "readiness_delta": c.readiness_delta,
                }
                for c in changes
            ],
        }

    def _get_current_readiness(self, user_id: str) -> float:
        role_analysis = self._role_analysis_repo.get_by_user_id(user_id)
        return role_analysis.readiness_score if role_analysis else 0

    def _record_changes(
        self,
        user_id: str,
        event_id: str,
        event_type: str,
        process_result: Dict[str, Any],
    ) -> list:
        changes = []

        if "skills_updated" in process_result:
            for skill_update in process_result["skills_updated"]:
                change = self._change_log_repo.create(
                    user_id=user_id,
                    event_id=event_id,
                    change_type="skill_confidence_changed",
                    skill_name=skill_update.get("skill_id", ""),
                    old_value={"confidence": skill_update.get("old_confidence", 0)},
                    new_value={"confidence": skill_update.get("new_confidence", 0)},
                    confidence_delta=skill_update.get("new_confidence", 0) - skill_update.get("old_confidence", 0),
                    explanation=f"Confidence changed from {skill_update.get('old_confidence', 0)}% to {skill_update.get('new_confidence', 0)}%",
                )
                changes.append(change)

        elif "skill_id" in process_result:
            change = self._change_log_repo.create(
                user_id=user_id,
                event_id=event_id,
                change_type="skill_confidence_changed",
                skill_name=process_result.get("skill_id", ""),
                old_value={"confidence": process_result.get("old_confidence", 0)},
                new_value={"confidence": process_result.get("new_confidence", 0)},
                confidence_delta=process_result.get("confidence_delta", 0),
                explanation=f"Confidence changed from {process_result.get('old_confidence', 0)}% to {process_result.get('new_confidence', 0)}%",
            )
            changes.append(change)

        return changes
