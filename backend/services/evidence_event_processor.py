import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.repositories import (
    CareerEvidenceEventRepository,
    SkillEvidenceRepository,
    UserSkillProfileRepository,
    CareerRoleAnalysisRepository,
    RoadmapRepository,
    GitHubProfileRepository,
    GitHubRepositoryEvidenceRepository,
)
from services.impact_analysis import ImpactAnalysis
from services.role_gap_analysis_service import RoleGapAnalysisService
from knowledge.loader import KnowledgeLoader

logger = logging.getLogger(__name__)


class EvidenceEventProcessor:
    def __init__(
        self,
        event_repo: Optional[CareerEvidenceEventRepository] = None,
        skill_evidence_repo: Optional[SkillEvidenceRepository] = None,
        skill_profile_repo: Optional[UserSkillProfileRepository] = None,
        role_analysis_repo: Optional[CareerRoleAnalysisRepository] = None,
        roadmap_repo: Optional[RoadmapRepository] = None,
        impact_analysis: Optional[ImpactAnalysis] = None,
        role_gap_service: Optional[RoleGapAnalysisService] = None,
        knowledge_loader: Optional[KnowledgeLoader] = None,
    ):
        self._event_repo = event_repo or CareerEvidenceEventRepository()
        self._skill_evidence_repo = skill_evidence_repo or SkillEvidenceRepository()
        self._skill_profile_repo = skill_profile_repo or UserSkillProfileRepository()
        self._role_analysis_repo = role_analysis_repo or CareerRoleAnalysisRepository()
        self._roadmap_repo = roadmap_repo or RoadmapRepository()
        self._impact = impact_analysis or ImpactAnalysis()
        self._role_gap = role_gap_service or RoleGapAnalysisService()
        self._knowledge = knowledge_loader or KnowledgeLoader()

    def create_event(
        self,
        user_id: str,
        event_type: str,
        event_data: dict = None,
        idempotency_key: str = None,
    ) -> Dict[str, Any]:
        if idempotency_key:
            existing = self._event_repo.get_by_idempotency_key(idempotency_key)
            if existing:
                return {
                    "event_id": str(existing.id),
                    "status": existing.status,
                    "duplicate": True,
                }

        event = self._event_repo.create(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data or {},
            idempotency_key=idempotency_key,
        )
        return {
            "event_id": str(event.id),
            "status": "pending",
            "duplicate": False,
        }

    def process_event(self, event_id: str) -> Dict[str, Any]:
        event = self._event_repo.get_by_id(event_id)
        if not event:
            return {"success": False, "error": "Event not found"}

        if event.status == "processed":
            return {"success": True, "message": "Already processed"}

        self._event_repo.update_status(event_id, "processing")

        try:
            event_type = event.event_type
            event_data = event.event_data or {}
            user_id = str(event.user_id)

            if event_type == "roadmap_skill_completed":
                result = self._process_skill_completed(user_id, event_data)
            elif event_type == "roadmap_project_completed":
                result = self._process_project_completed(user_id, event_data)
            elif event_type == "roadmap_certification_completed":
                result = self._process_certification_completed(user_id, event_data)
            elif event_type == "github_repository_linked":
                result = self._process_github_repo_linked(user_id, event_data)
            elif event_type == "github_repository_analyzed":
                result = self._process_github_repo_analyzed(user_id, event_data)
            elif event_type == "github_profile_reanalyzed":
                result = self._process_github_profile_reanalyzed(user_id, event_data)
            elif event_type == "assessment_completed":
                result = self._process_assessment_completed(user_id, event_data)
            elif event_type == "resume_uploaded":
                result = self._process_resume_uploaded(user_id, event_data)
            elif event_type == "certification_added":
                result = self._process_certification_added(user_id, event_data)
            elif event_type == "experience_added":
                result = self._process_experience_added(user_id, event_data)
            else:
                result = {"success": False, "error": f"Unknown event type: {event_type}"}

            if result.get("success"):
                self._event_repo.update_status(event_id, "processed")
            else:
                self._event_repo.update_status(event_id, "failed", result.get("error"))

            return result

        except Exception as e:
            logger.exception("Failed to process event %s: %s", event_id, e)
            self._event_repo.update_status(event_id, "failed", str(e))
            return {"success": False, "error": str(e)}

    def _process_skill_completed(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        skill_id = event_data.get("skill_id", "")
        skill_name = event_data.get("skill_name", skill_id)
        if not skill_id:
            return {"success": False, "error": "skill_id is required"}

        strength_info = self._impact.get_evidence_strength_for_event("roadmap_skill_completed")
        base_confidence = int(strength_info["base_strength"] * 100)

        existing = self._skill_evidence_repo.get_by_user_and_skill(user_id, skill_id)
        old_confidence = existing.confidence if existing else 0
        new_confidence = min(100, max(old_confidence, base_confidence))

        evidence_items = [{
            "skill_id": skill_id,
            "skill_name": skill_name,
            "category": event_data.get("category", "Unknown"),
            "confidence": new_confidence,
            "confidence_level": self._confidence_level(new_confidence),
            "sources": [{"source": "roadmap", "strength": strength_info["base_strength"]}],
            "evidence_count": (existing.evidence_count if existing else 0) + 1,
            "strongest_source": "roadmap",
        }]
        self._skill_evidence_repo.upsert_many(user_id, evidence_items)

        impacted = self._impact.get_impacted_skills(skill_id)
        impacted_roles = self._impact.get_impacted_roles(skill_id)

        return {
            "success": True,
            "skill_id": skill_id,
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
            "confidence_delta": new_confidence - old_confidence,
            "impacted_skills": impacted,
            "impacted_roles": impacted_roles,
            "evidence_type": strength_info["evidence_type"],
        }

    def _process_project_completed(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        skills = event_data.get("skills", [])
        if not skills:
            return {"success": False, "error": "skills list is required for project completion"}

        strength_info = self._impact.get_evidence_strength_for_event("roadmap_project_completed")
        base_confidence = int(strength_info["base_strength"] * 100)
        results = []

        for skill in skills:
            skill_id = skill if isinstance(skill, str) else skill.get("skill_id", "")
            skill_name = skill_id
            if not skill_id:
                continue

            existing = self._skill_evidence_repo.get_by_user_and_skill(user_id, skill_id)
            old_confidence = existing.confidence if existing else 0
            new_confidence = min(100, max(old_confidence, base_confidence))

            evidence_items = [{
                "skill_id": skill_id,
                "skill_name": skill_name,
                "confidence": new_confidence,
                "confidence_level": self._confidence_level(new_confidence),
                "sources": [{"source": "project", "strength": strength_info["base_strength"]}],
                "evidence_count": (existing.evidence_count if existing else 0) + 1,
                "strongest_source": "project",
            }]
            self._skill_evidence_repo.upsert_many(user_id, evidence_items)
            results.append({
                "skill_id": skill_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
            })

        return {
            "success": True,
            "skills_updated": results,
            "evidence_type": strength_info["evidence_type"],
        }

    def _process_certification_completed(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        cert_name = event_data.get("certification_name", "")
        skills = event_data.get("skills", [])
        if not cert_name:
            return {"success": False, "error": "certification_name is required"}

        strength_info = self._impact.get_evidence_strength_for_event("roadmap_certification_completed")
        base_confidence = int(strength_info["base_strength"] * 100)
        results = []

        for skill in skills:
            skill_id = skill if isinstance(skill, str) else skill.get("skill_id", "")
            if not skill_id:
                continue

            existing = self._skill_evidence_repo.get_by_user_and_skill(user_id, skill_id)
            old_confidence = existing.confidence if existing else 0
            new_confidence = min(100, max(old_confidence, base_confidence))

            evidence_items = [{
                "skill_id": skill_id,
                "skill_name": skill_id,
                "confidence": new_confidence,
                "confidence_level": self._confidence_level(new_confidence),
                "sources": [{"source": "certification", "cert_name": cert_name, "strength": strength_info["base_strength"]}],
                "evidence_count": (existing.evidence_count if existing else 0) + 1,
                "strongest_source": "certification",
            }]
            self._skill_evidence_repo.upsert_many(user_id, evidence_items)
            results.append({
                "skill_id": skill_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
            })

        return {
            "success": True,
            "certification_name": cert_name,
            "skills_updated": results,
            "evidence_type": strength_info["evidence_type"],
        }

    def _process_github_repo_linked(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        repo_name = event_data.get("repository_name", "")
        languages = event_data.get("languages", {})
        topics = event_data.get("topics", [])

        strength_info = self._impact.get_evidence_strength_for_event("github_repository_linked")
        base_confidence = int(strength_info["base_strength"] * 100)
        results = []

        all_skills = list(set(list(languages.keys()) + topics))
        for skill_name in all_skills:
            skill_id = skill_name
            existing = self._skill_evidence_repo.get_by_user_and_skill(user_id, skill_id)
            old_confidence = existing.confidence if existing else 0
            new_confidence = min(100, max(old_confidence, base_confidence))

            evidence_items = [{
                "skill_id": skill_id,
                "skill_name": skill_name,
                "confidence": new_confidence,
                "confidence_level": self._confidence_level(new_confidence),
                "sources": [{"source": "github", "repo": repo_name, "strength": strength_info["base_strength"]}],
                "evidence_count": (existing.evidence_count if existing else 0) + 1,
                "strongest_source": "github",
            }]
            self._skill_evidence_repo.upsert_many(user_id, evidence_items)
            results.append({
                "skill_id": skill_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
            })

        return {
            "success": True,
            "repository_name": repo_name,
            "skills_updated": results,
            "evidence_type": strength_info["evidence_type"],
        }

    def _process_github_repo_analyzed(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        return self._process_github_repo_linked(user_id, event_data)

    def _process_github_profile_reanalyzed(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        strength_info = self._impact.get_evidence_strength_for_event("github_profile_reanalyzed")
        base_confidence = int(strength_info["base_strength"] * 100)
        skills_from_profile = event_data.get("skills", [])
        results = []

        for skill_name in skills_from_profile:
            skill_id = skill_name
            existing = self._skill_evidence_repo.get_by_user_and_skill(user_id, skill_id)
            old_confidence = existing.confidence if existing else 0
            new_confidence = min(100, max(old_confidence, base_confidence))

            evidence_items = [{
                "skill_id": skill_id,
                "skill_name": skill_name,
                "confidence": new_confidence,
                "confidence_level": self._confidence_level(new_confidence),
                "sources": [{"source": "github_profile", "strength": strength_info["base_strength"]}],
                "evidence_count": (existing.evidence_count if existing else 0) + 1,
                "strongest_source": "github_profile",
            }]
            self._skill_evidence_repo.upsert_many(user_id, evidence_items)
            results.append({
                "skill_id": skill_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
            })

        return {
            "success": True,
            "skills_updated": results,
            "evidence_type": strength_info["evidence_type"],
        }

    def _process_assessment_completed(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        matched_skills = event_data.get("matched_skills", [])
        score = event_data.get("score", 0)
        strength_info = self._impact.get_evidence_strength_for_event("assessment_completed")
        base_confidence = int(strength_info["base_strength"] * 100)
        results = []

        for skill in matched_skills:
            skill_id = skill if isinstance(skill, str) else skill.get("skill_id", "")
            if not skill_id:
                continue

            existing = self._skill_evidence_repo.get_by_user_and_skill(user_id, skill_id)
            old_confidence = existing.confidence if existing else 0
            new_confidence = min(100, max(old_confidence, base_confidence))

            evidence_items = [{
                "skill_id": skill_id,
                "skill_name": skill_id,
                "confidence": new_confidence,
                "confidence_level": self._confidence_level(new_confidence),
                "sources": [{"source": "assessment", "score": score, "strength": strength_info["base_strength"]}],
                "evidence_count": (existing.evidence_count if existing else 0) + 1,
                "strongest_source": "assessment",
            }]
            self._skill_evidence_repo.upsert_many(user_id, evidence_items)
            results.append({
                "skill_id": skill_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
            })

        return {
            "success": True,
            "skills_updated": results,
            "evidence_type": strength_info["evidence_type"],
        }

    def _process_resume_uploaded(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        skills = event_data.get("skills", [])
        strength_info = self._impact.get_evidence_strength_for_event("resume_uploaded")
        base_confidence = int(strength_info["base_strength"] * 100)
        results = []

        for skill in skills:
            skill_id = skill if isinstance(skill, str) else skill.get("skill_id", "")
            if not skill_id:
                continue

            existing = self._skill_evidence_repo.get_by_user_and_skill(user_id, skill_id)
            old_confidence = existing.confidence if existing else 0
            new_confidence = min(100, max(old_confidence, base_confidence))

            evidence_items = [{
                "skill_id": skill_id,
                "skill_name": skill_id,
                "confidence": new_confidence,
                "confidence_level": self._confidence_level(new_confidence),
                "sources": [{"source": "resume", "strength": strength_info["base_strength"]}],
                "evidence_count": (existing.evidence_count if existing else 0) + 1,
                "strongest_source": "resume",
            }]
            self._skill_evidence_repo.upsert_many(user_id, evidence_items)
            results.append({
                "skill_id": skill_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
            })

        return {
            "success": True,
            "skills_updated": results,
            "evidence_type": strength_info["evidence_type"],
        }

    def _process_certification_added(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        return self._process_certification_completed(user_id, event_data)

    def _process_experience_added(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        skills = event_data.get("skills", [])
        strength_info = self._impact.get_evidence_strength_for_event("experience_added")
        base_confidence = int(strength_info["base_strength"] * 100)
        results = []

        for skill in skills:
            skill_id = skill if isinstance(skill, str) else skill.get("skill_id", "")
            if not skill_id:
                continue

            existing = self._skill_evidence_repo.get_by_user_and_skill(user_id, skill_id)
            old_confidence = existing.confidence if existing else 0
            new_confidence = min(100, max(old_confidence, base_confidence))

            evidence_items = [{
                "skill_id": skill_id,
                "skill_name": skill_id,
                "confidence": new_confidence,
                "confidence_level": self._confidence_level(new_confidence),
                "sources": [{"source": "experience", "strength": strength_info["base_strength"]}],
                "evidence_count": (existing.evidence_count if existing else 0) + 1,
                "strongest_source": "experience",
            }]
            self._skill_evidence_repo.upsert_many(user_id, evidence_items)
            results.append({
                "skill_id": skill_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
            })

        return {
            "success": True,
            "skills_updated": results,
            "evidence_type": strength_info["evidence_type"],
        }

    def _confidence_level(self, confidence: int) -> str:
        if confidence >= 80:
            return "high"
        elif confidence >= 60:
            return "medium"
        elif confidence >= 40:
            return "low"
        return "minimal"
