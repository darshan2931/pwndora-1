import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime

from models.sqlalchemy_models import (
    CareerOpportunity, OpportunityRequirement, OpportunityMatch,
    SkillEvidence, UserSkillLevel, Assessment,
)
from repositories.opportunity_repositories import (
    CareerOpportunityRepository,
    OpportunityRequirementRepository,
    OpportunityMatchRepository,
)
from services.role_gap_config import SkillImportance

logger = logging.getLogger(__name__)


class OpportunityMatchingService:
    """
    Deterministic matching engine that compares user evidence against
    curated cybersecurity job opportunities with explainable scores.
    """

    WEIGHTS = {
        "required_skill_coverage": 0.40,
        "evidence_strength": 0.20,
        "project_relevance": 0.15,
        "certification_alignment": 0.10,
        "experience_alignment": 0.05,
    }

    CATEGORIES = {
        "highly_eligible": (80, 100),
        "strong_contender": (60, 79),
        "developing_candidate": (40, 59),
        "early_gap": (0, 39),
    }

    IMPORTANCE_SCORES = {
        "critical": 100,
        "high": 90,
        "important": 70,
        "medium": 50,
        "low": 30,
        "beneficial": 20,
    }

    def __init__(self):
        self.opp_repo = CareerOpportunityRepository()
        self.req_repo = OpportunityRequirementRepository()
        self.match_repo = OpportunityMatchRepository()

    def get_all_opportunities(self) -> List[CareerOpportunity]:
        return self.opp_repo.get_all_active()

    def get_opportunity_by_id(self, opportunity_id: str) -> Optional[CareerOpportunity]:
        return self.opp_repo.get_by_id(opportunity_id)

    def get_user_matches(self, user_id: str) -> List[Dict]:
        matches = self.match_repo.get_by_user_id(user_id)
        results = []
        for match in matches:
            opp = self.opp_repo.get_by_id(str(match.opportunity_id))
            if opp:
                results.append({
                    "match": match,
                    "opportunity": opp,
                })
        return results

    def get_user_match(self, user_id: str, opportunity_id: str) -> Optional[Dict]:
        match = self.match_repo.get_by_user_and_opportunity(user_id, opportunity_id)
        opp = self.opp_repo.get_by_id(opportunity_id)
        if match and opp:
            return {"match": match, "opportunity": opp}
        return None

    def calculate_match(
        self,
        user_id: str,
        opportunity_id: str,
        user_evidence: List[SkillEvidence],
        user_certifications: List[str],
    ) -> Dict:
        opp = self.opp_repo.get_by_id(opportunity_id)
        if not opp:
            return {"error": "Opportunity not found"}

        requirements = self.req_repo.get_by_opportunity_id(opportunity_id)
        required = [r for r in requirements if r.requirement_type == "required"]
        preferred = [r for r in requirements if r.requirement_type == "preferred"]
        certs = [r for r in requirements if r.requirement_type == "certification"]

        evidence_map = self._build_evidence_map(user_evidence)

        required_coverage = self._compute_skill_coverage(required, evidence_map)
        preferred_coverage = self._compute_skill_coverage(preferred, evidence_map)
        evidence_strength = self._compute_evidence_strength(required, evidence_map)
        project_relevance = self._compute_project_relevance(required, evidence_map)
        cert_score = self._compute_cert_alignment(certs, user_certifications)
        experience_score = self._compute_experience_alignment(required, evidence_map)

        missing = self._identify_missing_skills(required, evidence_map)
        strengths = self._identify_strengths(required, evidence_map)

        total_score = round(
            self.WEIGHTS["required_skill_coverage"] * required_coverage
            + self.WEIGHTS["evidence_strength"] * evidence_strength
            + self.WEIGHTS["project_relevance"] * project_relevance
            + self.WEIGHTS["certification_alignment"] * cert_score
            + self.WEIGHTS["experience_alignment"] * experience_score
        )
        total_score = max(0, min(100, total_score))

        category = self._categorize_match(total_score)
        recommendation = self._generate_recommendation(category, missing, strengths)

        match_data = {
            "match_score": total_score,
            "required_skill_coverage": round(required_coverage),
            "preferred_skill_coverage": round(preferred_coverage),
            "evidence_score": round(evidence_strength),
            "certification_score": round(cert_score),
            "missing_skills": missing,
            "strengths": strengths,
            "match_category": category,
            "recommendation": recommendation,
        }

        saved = self.match_repo.upsert(user_id, opportunity_id, **match_data)

        return {
            "match_id": str(saved.id),
            "opportunity_id": opportunity_id,
            "opportunity_title": opp.title,
            "organization": opp.organization,
            "overall_score": total_score,
            "category": category,
            "breakdown": {
                "required_skill_coverage": round(required_coverage),
                "preferred_skill_coverage": round(preferred_coverage),
                "evidence_strength": round(evidence_strength),
                "project_relevance": round(project_relevance),
                "certification_alignment": round(cert_score),
                "experience_alignment": round(experience_score),
            },
            "missing_skills": missing,
            "strengths": strengths,
            "recommendation": recommendation,
            "weights": self.WEIGHTS,
        }

    def calculate_all_matches(
        self,
        user_id: str,
        user_evidence: List[SkillEvidence],
        user_certifications: List[str],
    ) -> List[Dict]:
        opportunities = self.get_all_opportunities()
        results = []
        for opp in opportunities:
            result = self.calculate_match(
                user_id, str(opp.id), user_evidence, user_certifications
            )
            if "error" not in result:
                results.append(result)
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        return results

    def _build_evidence_map(self, evidence: List[SkillEvidence]) -> Dict[str, List[SkillEvidence]]:
        evidence_map: Dict[str, List[SkillEvidence]] = {}
        for ev in evidence:
            skill_name = ev.skill_name.lower().strip()
            if skill_name not in evidence_map:
                evidence_map[skill_name] = []
            evidence_map[skill_name].append(ev)
        return evidence_map

    def _compute_skill_coverage(
        self, requirements: List[OpportunityRequirement], evidence_map: Dict
    ) -> float:
        if not requirements:
            return 100.0
        total_weight = 0
        covered_weight = 0
        for req in requirements:
            score = self.IMPORTANCE_SCORES.get(req.importance, 50)
            total_weight += score
            if req.skill_name.lower() in evidence_map:
                covered_weight += score
        return (covered_weight / total_weight * 100) if total_weight > 0 else 0

    def _compute_evidence_strength(
        self, requirements: List[OpportunityRequirement], evidence_map: Dict
    ) -> float:
        if not requirements:
            return 100.0
        scores = []
        for req in requirements:
            skill_evidence = evidence_map.get(req.skill_name.lower(), [])
            if skill_evidence:
                max_conf = max(e.confidence for e in skill_evidence)
                scores.append(max_conf)
            else:
                scores.append(0)
        return sum(scores) / len(scores) if scores else 0

    def _compute_project_relevance(
        self, requirements: List[OpportunityRequirement], evidence_map: Dict
    ) -> float:
        project_skills = 0
        covered_project = 0
        for req in requirements:
            if req.importance in ("critical", "high", "important"):
                project_skills += 1
                skill_evidence = evidence_map.get(req.skill_name.lower(), [])
                if skill_evidence:
                    has_project = False
                    for e in skill_evidence:
                        if hasattr(e, 'sources') and e.sources:
                            for src in e.sources:
                                if isinstance(src, dict) and src.get("source") in ("project", "github", "lab"):
                                    has_project = True
                                    break
                        if hasattr(e, 'strongest_source') and e.strongest_source in ("project", "github", "lab"):
                            has_project = True
                            break
                    if has_project:
                        covered_project += 1
        return (covered_project / project_skills * 100) if project_skills > 0 else 0

    def _compute_cert_alignment(
        self, cert_requirements: List[OpportunityRequirement], user_certs: List[str]
    ) -> float:
        if not cert_requirements:
            return 100.0
        matched = 0
        user_lower = [c.lower().strip() for c in user_certs]
        for req in cert_requirements:
            req_lower = req.skill_name.lower().strip()
            if any(req_lower in uc or uc in req_lower for uc in user_lower):
                matched += 1
        return (matched / len(cert_requirements) * 100) if cert_requirements else 0

    def _compute_experience_alignment(
        self, requirements: List[OpportunityRequirement], evidence_map: Dict
    ) -> float:
        if not requirements:
            return 100.0
        total_evidence = 0
        for req in requirements:
            skill_evidence = evidence_map.get(req.skill_name.lower(), [])
            total_evidence += len(skill_evidence)
        avg_per_skill = total_evidence / len(requirements) if requirements else 0
        return min(100, avg_per_skill * 30)

    def _identify_missing_skills(
        self, requirements: List[OpportunityRequirement], evidence_map: Dict
    ) -> List[Dict]:
        missing = []
        for req in requirements:
            if req.skill_name.lower() not in evidence_map:
                missing.append({
                    "skill": req.skill_name,
                    "importance": req.importance,
                    "importance_score": self.IMPORTANCE_SCORES.get(req.importance, 50),
                    "requirement_type": req.requirement_type,
                })
        missing.sort(key=lambda x: x["importance_score"], reverse=True)
        return missing

    def _identify_strengths(
        self, requirements: List[OpportunityRequirement], evidence_map: Dict
    ) -> List[Dict]:
        strengths = []
        for req in requirements:
            skill_evidence = evidence_map.get(req.skill_name.lower(), [])
            if skill_evidence:
                max_conf = max(e.confidence for e in skill_evidence)
                evidence_types = []
                for e in skill_evidence:
                    if hasattr(e, 'strongest_source') and e.strongest_source:
                        if e.strongest_source not in evidence_types:
                            evidence_types.append(e.strongest_source)
                    elif hasattr(e, 'sources') and e.sources:
                        for src in e.sources:
                            if isinstance(src, dict) and src.get("source"):
                                if src["source"] not in evidence_types:
                                    evidence_types.append(src["source"])
                strengths.append({
                    "skill": req.skill_name,
                    "importance": req.importance,
                    "max_confidence": max_conf,
                    "evidence_count": len(skill_evidence),
                    "evidence_types": evidence_types,
                })
        strengths.sort(key=lambda x: x["max_confidence"], reverse=True)
        return strengths

    def _categorize_match(self, score: int) -> str:
        for category, (low, high) in self.CATEGORIES.items():
            if low <= score <= high:
                return category
        return "early_gap"

    def _generate_recommendation(
        self, category: str, missing: List[Dict], strengths: List[Dict]
    ) -> str:
        if category == "highly_eligible":
            return "Strong match. Consider applying and highlighting your key strengths."
        elif category == "strong_contender":
            top_missing = [m["skill"] for m in missing[:2]]
            if top_missing:
                return f"Good match. Focus on: {', '.join(top_missing)} to strengthen your candidacy."
            return "Good match with solid coverage across requirements."
        elif category == "developing_candidate":
            top_missing = [m["skill"] for m in missing[:3]]
            if top_missing:
                return f"Developing match. Priority skills to build: {', '.join(top_missing)}."
            return "Developing match. Continue building core skills."
        else:
            top_missing = [m["skill"] for m in missing[:3]]
            if top_missing:
                return f"Early-stage match. Foundation skills needed: {', '.join(top_missing)}."
            return "Early-stage match. Focus on building foundational skills."
