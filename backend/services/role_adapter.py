from typing import Any, Dict, List, Optional

from services.role_gap_config import (
    get_importance_level,
    get_importance_score,
    get_minimum_confidence,
)
from knowledge.loader import KnowledgeLoader


class RoleAdapter:
    def __init__(self, knowledge_loader: Optional[KnowledgeLoader] = None):
        self._knowledge_loader = knowledge_loader or KnowledgeLoader()

    def get_role_enriched(self, role_id: str) -> Optional[Dict[str, Any]]:
        role = self._knowledge_loader.get_role(role_id)
        if not role:
            return None
        return self._enrich_role(role, role_id)

    def get_all_roles_enriched(self) -> List[Dict[str, Any]]:
        roles = self._knowledge_loader.get_roles()
        enriched = []
        for role in roles:
            role_name = role.get("role", "")
            enriched.append(self._enrich_role(role, role_name))
        return enriched

    def _enrich_role(self, role: Dict[str, Any], role_id: str) -> Dict[str, Any]:
        required_skills = role.get("required_skills", [])
        optional_skills = role.get("optional_skills", [])

        enriched_required = []
        for skill_name in required_skills:
            importance = get_importance_level(role_id, skill_name, is_required=True)
            enriched_required.append({
                "skill_name": skill_name,
                "importance": importance.name,
                "importance_score": importance.value,
                "minimum_confidence": get_minimum_confidence(role_id, skill_name, is_required=True),
                "is_required": True,
            })

        enriched_optional = []
        for skill_name in optional_skills:
            importance = get_importance_level(role_id, skill_name, is_required=False)
            enriched_optional.append({
                "skill_name": skill_name,
                "importance": importance.name,
                "importance_score": importance.value,
                "minimum_confidence": get_minimum_confidence(role_id, skill_name, is_required=False),
                "is_required": False,
            })

        return {
            "role_id": role_id,
            "role_name": role.get("role", role_id),
            "description": role.get("description", ""),
            "required_skills": enriched_required,
            "optional_skills": enriched_optional,
            "recommended_certifications": role.get("recommended_certifications", []),
            "suggested_projects": role.get("suggested_projects", []),
            "estimated_duration": role.get("estimated_duration", None),
        }

    def get_skill_importance_for_role(self, role_id: str, skill_id: str) -> float:
        role = self._knowledge_loader.get_role(role_id)
        if not role:
            return 0.5

        required_skills = role.get("required_skills", [])
        optional_skills = role.get("optional_skills", [])
        skill_lower = skill_id.lower()

        if skill_id in required_skills or skill_lower in [s.lower() for s in required_skills]:
            return get_importance_score(role_id, skill_id, is_required=True)
        elif skill_id in optional_skills or skill_lower in [s.lower() for s in optional_skills]:
            return get_importance_score(role_id, skill_id, is_required=False)
        return 0.0

    def get_min_confidence_for_role(self, role_id: str, skill_id: str) -> float:
        role = self._knowledge_loader.get_role(role_id)
        if not role:
            return 0.5

        required_skills = role.get("required_skills", [])
        optional_skills = role.get("optional_skills", [])
        skill_lower = skill_id.lower()

        if skill_id in required_skills or skill_lower in [s.lower() for s in required_skills]:
            return get_minimum_confidence(role_id, skill_id, is_required=True)
        elif skill_id in optional_skills or skill_lower in [s.lower() for s in optional_skills]:
            return get_minimum_confidence(role_id, skill_id, is_required=False)
        return 0.5
