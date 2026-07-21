import logging
from typing import Any, Dict, List, Optional, Tuple

from services.role_gap_config import GapStatus, PriorityLevel, SkillImportance
from services.role_adapter import RoleAdapter
from knowledge.loader import KnowledgeLoader

logger = logging.getLogger(__name__)


class GapAnalysisService:
    def __init__(
        self,
        role_adapter: Optional[RoleAdapter] = None,
        knowledge_loader: Optional[KnowledgeLoader] = None,
    ):
        self._role_adapter = role_adapter or RoleAdapter()
        self._knowledge_loader = knowledge_loader or KnowledgeLoader()
        self._skills_data = None

    @property
    def skills_data(self) -> Dict[str, Any]:
        if self._skills_data is None:
            raw = self._knowledge_loader.get_skills() or []
            self._skills_data = {s["name"]: s for s in raw if "name" in s}
        return self._skills_data

    def calculate_skill_gap(
        self,
        role_id: str,
        skill_id: str,
        current_confidence: float,
        is_required: bool,
    ) -> Dict[str, Any]:
        importance_score = self._role_adapter.get_skill_importance_for_role(role_id, skill_id)
        minimum_confidence = self._role_adapter.get_min_confidence_for_role(role_id, skill_id)

        gap_size = max(0, minimum_confidence - current_confidence)

        gap_status = self._classify_gap_status(current_confidence, minimum_confidence)

        importance = self._get_importance_enum(importance_score)

        skill_data = self.skills_data.get(skill_id, {})
        category = skill_data.get("category", "Unknown")
        prerequisites = skill_data.get("prerequisites", [])

        return {
            "skill_id": skill_id,
            "skill_name": skill_id,
            "category": category,
            "confidence": current_confidence,
            "minimum_confidence": minimum_confidence,
            "gap_size": gap_size,
            "gap_status": gap_status.value,
            "importance": importance.value,
            "importance_score": importance_score,
            "is_required": is_required,
            "has_prerequisites": len(prerequisites) > 0,
            "blocked_by": prerequisites,
            "evidence_sources": [],
        }

    def _classify_gap_status(self, current_confidence: float, minimum_confidence: float) -> GapStatus:
        if current_confidence >= minimum_confidence:
            return GapStatus.COVERED
        ratio = current_confidence / minimum_confidence if minimum_confidence > 0 else 0

        if ratio >= 0.75:
            return GapStatus.MINIMAL
        elif ratio >= 0.40:
            return GapStatus.PARTIAL
        elif ratio >= 0.15:
            return GapStatus.CRITICAL
        return GapStatus.MISSING

    def _get_importance_enum(self, score: float) -> SkillImportance:
        if score >= 0.85:
            return SkillImportance.REQUIRED
        elif score >= 0.65:
            return SkillImportance.CRITICAL
        elif score >= 0.45:
            return SkillImportance.IMPORTANT
        return SkillImportance.BENEFICIAL

    def calculate_priority_score(self, gap: Dict[str, Any]) -> float:
        gap_size = gap["gap_size"]
        importance_score = gap["importance_score"]

        prerequisite_impact = self._calculate_prerequisite_impact(gap["skill_id"])
        career_relevance = self._calculate_career_relevance(gap["skill_id"], gap["is_required"])

        priority = (
            gap_size * 0.40
            + importance_score * 0.30
            + prerequisite_impact * 0.20
            + career_relevance * 0.10
        )

        return round(min(1.0, max(0.0, priority)), 4)

    def _calculate_prerequisite_impact(self, skill_id: str) -> float:
        unblocked = self._get_unblocked_skills(skill_id)
        if not unblocked:
            return 0.1

        impact = min(1.0, 0.1 + len(unblocked) * 0.05)
        return round(impact, 4)

    def _calculate_career_relevance(self, skill_id: str, is_required: bool) -> float:
        roles_requiring = self._count_roles_requiring_skill(skill_id)
        total_roles = len(self._knowledge_loader.get_roles() or {})
        if total_roles == 0:
            return 0.5

        relevance = roles_requiring / total_roles
        if is_required:
            relevance = min(1.0, relevance * 1.5)

        return round(min(1.0, relevance), 4)

    def _count_roles_requiring_skill(self, skill_id: str) -> int:
        roles = self._knowledge_loader.get_roles() or []
        count = 0
        for role_data in roles:
            required = role_data.get("required_skills", [])
            optional = role_data.get("optional_skills", [])
            if skill_id in required or skill_id in optional:
                count += 1
        return count

    def _get_unblocked_skills(self, skill_id: str) -> List[str]:
        all_skills = self.skills_data
        unblocked = []
        for sid, sdata in all_skills.items():
            prereqs = sdata.get("prerequisites", [])
            if skill_id in prereqs:
                unblocked.append(sid)
        return unblocked

    def get_blocked_skills(self, skill_id: str) -> List[str]:
        skill_data = self.skills_data.get(skill_id, {})
        return skill_data.get("prerequisites", [])

    def build_dependency_graph(self, skill_ids: List[str]) -> Dict[str, List[str]]:
        graph = {}
        for sid in skill_ids:
            skill_data = self.skills_data.get(sid, {})
            prerequisites = skill_data.get("prerequisites", [])
            graph[sid] = [p for p in prerequisites if p in skill_ids]
        return graph

    def check_prerequisites_met(
        self, skill_id: str, covered_skills: set
    ) -> Tuple[bool, List[str]]:
        skill_data = self.skills_data.get(skill_id, {})
        prerequisites = skill_data.get("prerequisites", [])
        blockers = [p for p in prerequisites if p not in covered_skills]
        return len(blockers) == 0, blockers

    def calculate_readiness(
        self,
        role_id: str,
        skill_confidences: Dict[str, float],
    ) -> Dict[str, Any]:
        role_enriched = self._role_adapter.get_role_enriched(role_id)
        if not role_enriched:
            return {
                "overall_readiness": 0.0,
                "required_skills": {},
                "optional_skills": {},
            }

        required_skills = role_enriched.get("required_skills", [])
        optional_skills = role_enriched.get("optional_skills", [])

        req_results = {}
        total_required_weight = 0.0
        weighted_required_confidence = 0.0

        for req in required_skills:
            skill_id = req["skill_name"]
            confidence = skill_confidences.get(skill_id, 0.0)
            importance_score = req["importance_score"]
            min_conf = req["minimum_confidence"]

            req_results[skill_id] = {
                "confidence": confidence,
                "importance": req["importance"],
                "importance_score": importance_score,
                "minimum_confidence": min_conf,
                "meets_minimum": confidence >= min_conf,
            }
            total_required_weight += importance_score
            weighted_required_confidence += confidence * importance_score

        opt_results = {}
        total_optional_weight = 0.0
        weighted_optional_confidence = 0.0

        for opt in optional_skills:
            skill_id = opt["skill_name"]
            confidence = skill_confidences.get(skill_id, 0.0)
            importance_score = opt["importance_score"]

            opt_results[skill_id] = {
                "confidence": confidence,
                "importance": opt["importance"],
                "importance_score": importance_score,
            }
            total_optional_weight += importance_score
            weighted_optional_confidence += confidence * importance_score

        if total_required_weight > 0:
            required_readiness = weighted_required_confidence / total_required_weight
        else:
            required_readiness = 0.0

        if total_optional_weight > 0:
            optional_readiness = weighted_optional_confidence / total_optional_weight
        else:
            optional_readiness = 0.0

        overall = required_readiness * 0.75 + optional_readiness * 0.25

        return {
            "overall_readiness": round(min(1.0, overall), 4),
            "required_skills": req_results,
            "optional_skills": opt_results,
        }

    def determine_readiness_level(self, score: float) -> str:
        if score >= 0.85:
            return "excellent"
        elif score >= 0.70:
            return "good"
        elif score >= 0.50:
            return "developing"
        elif score >= 0.25:
            return "beginning"
        return "not_started"

    def get_learning_path_for_role(self, role_id: str) -> List[Dict[str, Any]]:
        roles = self._knowledge_loader.get_roles()
        if not roles:
            return []

        role = None
        for r in roles:
            if r.get("role", "").lower() == role_id.lower():
                role = r
                break
        if not role:
            return []

        required_skills = role.get("required_skills", [])

        sorted_skills = self._topological_sort_skills(required_skills)

        path = []
        for i, skill_id in enumerate(sorted_skills):
            skill_data = self.skills_data.get(skill_id, {})
            path.append({
                "order": i + 1,
                "skill_id": skill_id,
                "skill_name": skill_id,
                "category": skill_data.get("category", "Unknown"),
                "estimated_hours": skill_data.get("estimated_hours", 0),
                "difficulty": skill_data.get("difficulty", "Intermediate"),
                "prerequisites": skill_data.get("prerequisites", []),
            })

        return path

    def _topological_sort_skills(self, skill_ids: List[str]) -> List[str]:
        visited = set()
        result = []

        def dfs(skill_id: str):
            if skill_id in visited:
                return
            visited.add(skill_id)

            skill_data = self.skills_data.get(skill_id, {})
            prerequisites = skill_data.get("prerequisites", [])
            for prereq in prerequisites:
                if prereq in skill_ids:
                    dfs(prereq)

            result.append(skill_id)

        for sid in skill_ids:
            dfs(sid)

        return result

    def find_next_skill(
        self,
        role_id: str,
        skill_confidences: Dict[str, float],
    ) -> Optional[Dict[str, Any]]:
        role_enriched = self._role_adapter.get_role_enriched(role_id)
        if not role_enriched:
            return None

        all_skills = []
        covered_skills = set()

        for req in role_enriched["required_skills"]:
            skill_id = req["skill_name"]
            confidence = skill_confidences.get(skill_id, 0.0)
            min_conf = req["minimum_confidence"]
            gap_size = max(0, min_conf - confidence)

            if confidence >= min_conf:
                covered_skills.add(skill_id)
                continue

            all_skills.append({
                "skill_id": skill_id,
                "skill_name": skill_id,
                "category": self.skills_data.get(skill_id, {}).get("category", "Unknown"),
                "confidence": confidence,
                "gap_size": gap_size,
                "importance": req["importance"],
                "importance_score": req["importance_score"],
                "is_required": True,
            })

        for opt in role_enriched["optional_skills"]:
            skill_id = opt["skill_name"]
            confidence = skill_confidences.get(skill_id, 0.0)
            min_conf = opt["minimum_confidence"]
            gap_size = max(0, min_conf - confidence)

            if confidence >= min_conf:
                covered_skills.add(skill_id)
                continue

            all_skills.append({
                "skill_id": skill_id,
                "skill_name": skill_id,
                "category": self.skills_data.get(skill_id, {}).get("category", "Unknown"),
                "confidence": confidence,
                "gap_size": gap_size,
                "importance": opt["importance"],
                "importance_score": opt["importance_score"],
                "is_required": False,
            })

        for skill in all_skills:
            skill["priority_score"] = self.calculate_priority_score(skill)
            prereqs_met, blockers = self.check_prerequisites_met(
                skill["skill_id"], covered_skills
            )
            skill["prerequisites_met"] = prereqs_met
            skill["blockers"] = blockers

            if not prereqs_met:
                skill["priority_score"] *= 0.3

        all_skills.sort(key=lambda s: s["priority_score"], reverse=True)

        if not all_skills:
            return None

        best = all_skills[0]
        skill_data = self.skills_data.get(best["skill_id"], {})

        return {
            "skill_id": best["skill_id"],
            "skill_name": best["skill_name"],
            "category": best["category"],
            "confidence": best["confidence"],
            "gap_size": best["gap_size"],
            "importance": best["importance"],
            "priority_score": best["priority_score"],
            "estimated_hours": skill_data.get("estimated_hours"),
            "prerequisites_met": best["prerequisites_met"],
            "blockers": best["blockers"],
            "recommendation_reason": self._build_recommendation_reason(best),
            "learning_resources": skill_data.get("learning_resources", []),
        }

    def _build_recommendation_reason(self, skill: Dict[str, Any]) -> str:
        parts = []

        if skill["gap_size"] >= 0.5:
            parts.append(f"Large gap ({skill['gap_size']:.0%} from minimum)")
        elif skill["gap_size"] >= 0.25:
            parts.append(f"Moderate gap ({skill['gap_size']:.0%} from minimum)")
        else:
            parts.append(f"Small gap ({skill['gap_size']:.0%} from minimum)")

        if skill["importance"] in ("required", "critical"):
            parts.append(f"{skill['importance'].title()} skill for this role")
        elif skill["importance"] == "important":
            parts.append("Important skill for career growth")

        unblocked = self._get_unblocked_skills(skill["skill_id"])
        if len(unblocked) >= 3:
            parts.append(f"Unlocks {len(unblocked)} other skills")
        elif len(unblocked) > 0:
            parts.append(f"Prerequisite for {len(unblocked)} other skill{'s' if len(unblocked) > 1 else ''}")

        if not skill.get("prerequisites_met", True):
            parts.append(f"Blocked by: {', '.join(skill.get('blocked_by', []))}")

        return ". ".join(parts) if parts else "Recommended next step"
