import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

from services.skill_normalization_service import skill_normalizer
from services.skill_evidence_aggregation_service import (
    EvidenceItem,
    AggregatedSkillEvidence,
    aggregation_service,
)
from services.evidence_config import EvidenceSource

logger = logging.getLogger(__name__)


class SkillEvidenceOrchestrator:

    def analyze_user(self, user_id: str) -> Dict[str, AggregatedSkillEvidence]:
        evidence_items: List[EvidenceItem] = []

        evidence_items.extend(self._collect_resume_evidence(user_id))
        evidence_items.extend(self._collect_github_evidence(user_id))
        evidence_items.extend(self._collect_assessment_evidence(user_id))

        results = aggregation_service.aggregate(evidence_items)
        logger.info(
            "Skill evidence analysis for user %s: %d items -> %d skills",
            user_id, len(evidence_items), len(results),
        )
        return results

    def _collect_resume_evidence(self, user_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        try:
            from repositories.repositories import ResumeProfileRepository
            repo = ResumeProfileRepository()
            profile = repo.get_latest_by_user_id(user_id)
            if not profile or profile.processing_status != "completed":
                return items

            extracted = profile.extracted_profile or {}
            skills = extracted.get("skills", [])
            for skill_entry in skills:
                name = skill_entry.get("name") if isinstance(skill_entry, dict) else str(skill_entry)
                if not name:
                    continue
                items.append(EvidenceItem(
                    skill_name=name,
                    source=EvidenceSource.RESUME_CLAIM,
                    confidence=0.5,
                    details={"source_context": "resume_skills"},
                ))

            experience = extracted.get("experience", [])
            for exp in experience:
                if not isinstance(exp, dict):
                    continue
                techs = exp.get("technologies", [])
                role_desc = exp.get("description", "")
                for tech in techs:
                    if not tech:
                        continue
                    items.append(EvidenceItem(
                        skill_name=tech,
                        source=EvidenceSource.RESUME_EXPERIENCE,
                        confidence=0.6,
                        details={
                            "company": exp.get("company", ""),
                            "role": exp.get("role", ""),
                            "description_snippet": role_desc[:200] if role_desc else "",
                        },
                    ))

        except Exception as e:
            logger.warning("Failed to collect resume evidence for user %s: %s", user_id, e)
        return items

    def _collect_github_evidence(self, user_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        try:
            from repositories.repositories import (
                GitHubProfileRepository,
                GitHubRepositoryEvidenceRepository,
            )
            gh_profile_repo = GitHubProfileRepository()
            gh_evidence_repo = GitHubRepositoryEvidenceRepository()

            profile = gh_profile_repo.get_latest_by_user_id(user_id)
            if not profile or profile.processing_status != "completed":
                return items

            repo_evidences = gh_evidence_repo.get_by_profile_id(str(profile.id))

            for repo_ev in repo_evidences:
                repo_name = repo_ev.repository_name
                languages = repo_ev.languages or {}
                topics = repo_ev.topics or []
                tech_evidence = repo_ev.tech_evidence or []
                ai_analysis = repo_ev.ai_analysis or {}

                for lang in languages:
                    items.append(EvidenceItem(
                        skill_name=lang,
                        source=EvidenceSource.GITHUB_LANGUAGE,
                        confidence=0.6,
                        repository=repo_name,
                        details={"bytes": languages[lang]},
                    ))

                for topic in topics:
                    items.append(EvidenceItem(
                        skill_name=topic,
                        source=EvidenceSource.GITHUB_TOPIC,
                        confidence=0.4,
                        repository=repo_name,
                        details={"topic": topic},
                    ))

                for te in tech_evidence:
                    if isinstance(te, dict):
                        items.append(EvidenceItem(
                            skill_name=te.get("technology", ""),
                            source=EvidenceSource.GITHUB_README,
                            confidence=0.35,
                            repository=repo_name,
                            evidence_text=te.get("evidence_type", ""),
                            details=te.get("details", {}),
                        ))

                demonstrated = ai_analysis.get("demonstrated_technologies", [])
                for demo in demonstrated:
                    if isinstance(demo, dict) and demo.get("name"):
                        items.append(EvidenceItem(
                            skill_name=demo["name"],
                            source=EvidenceSource.GITHUB_AI_ANALYSIS,
                            confidence=0.55,
                            repository=repo_name,
                            evidence_text=demo.get("evidence", ""),
                            details={"project_purpose": ai_analysis.get("project_purpose", "")},
                        ))

        except Exception as e:
            logger.warning("Failed to collect github evidence for user %s: %s", user_id, e)
        return items

    def _collect_assessment_evidence(self, user_id: str) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        try:
            from repositories.repositories import AssessmentRepository
            repo = AssessmentRepository()
            assessments = repo.get_by_user_id(user_id)

            if not assessments:
                return items

            assessment = assessments[0] if isinstance(assessments, list) else assessments

            matched = assessment.matched_skills or []
            for skill_name in matched:
                items.append(EvidenceItem(
                    skill_name=skill_name,
                    source=EvidenceSource.ASSESSMENT_MATCHED,
                    confidence=0.5,
                    details={"assessment_id": str(assessment.id), "readiness_score": assessment.readiness_score},
                ))

        except Exception as e:
            logger.warning("Failed to collect assessment evidence for user %s: %s", user_id, e)
        return items

    def get_evidence_summary(
        self,
        results: Dict[str, AggregatedSkillEvidence],
    ) -> Dict:
        high = [s for s in results.values() if s.confidence_level == "high"]
        medium = [s for s in results.values() if s.confidence_level == "medium"]
        low = [s for s in results.values() if s.confidence_level == "low"]
        minimal = [s for s in results.values() if s.confidence_level == "minimal"]

        return {
            "total_skills": len(results),
            "high_confidence": len(high),
            "medium_confidence": len(medium),
            "low_confidence": len(low),
            "minimal_confidence": len(minimal),
            "skills": [
                {
                    "skill_id": s.skill_id,
                    "skill_name": s.skill_name,
                    "category": s.category,
                    "confidence": s.confidence,
                    "confidence_level": s.confidence_level,
                    "evidence_count": s.evidence_count,
                    "strongest_source": s.strongest_source,
                }
                for s in sorted(results.values(), key=lambda x: x.confidence, reverse=True)
            ],
        }


skill_evidence_orchestrator = SkillEvidenceOrchestrator()
