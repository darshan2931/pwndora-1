import logging
from typing import Tuple

from app.domain.models import Assessment, Career, Skill, UserProfile
from knowledge.loader import knowledge_loader
from services.service_interfaces import CareerService as ICareerService

logger = logging.getLogger(__name__)


class CareerService(ICareerService):
    def __init__(self):
        self.kb = knowledge_loader

    def analyze(self, user_skills: list[str], career_goal: str) -> Assessment:
        role_data = self.kb.get_role(career_goal)
        if not role_data:
            logger.warning("Unknown career goal: %s", career_goal)
            role_data = {
                "role": career_goal,
                "description": "",
                "required_skills": [],
                "optional_skills": [],
            }

        career = Career(
            id=career_goal.lower().replace(" ", "-"),
            title=career_goal,
            description=role_data.get("description", ""),
            required_skills=role_data.get("required_skills", []),
            optional_skills=role_data.get("optional_skills", []),
            recommended_certifications=role_data.get("recommended_certifications", []),
            suggested_projects=role_data.get("suggested_projects", []),
        )

        matched, missing = self._match_skills(user_skills, career)
        all_required = career.required_skills + career.optional_skills
        readiness = self.calculate_readiness(len(matched), len(all_required))

        profile = UserProfile(
            skills=[Skill(name=s, category="", difficulty="") for s in user_skills]
        )

        return Assessment(
            user_profile=profile,
            target_career=career,
            matched_skills=matched,
            missing_skills=missing,
            readiness_score=readiness,
        )

    def _match_skills(
        self, user_skills: list[str], career: Career
    ) -> Tuple[list[Skill], list[Skill]]:
        all_required = career.required_skills + career.optional_skills
        user_skills_lower = [s.lower() for s in user_skills]

        matched = []
        missing = []

        for skill_name in all_required:
            skill_data = self.kb.get_skill(skill_name) or {
                "name": skill_name,
                "category": "",
                "difficulty": "intermediate",
            }
            if skill_name.lower() in user_skills_lower:
                matched.append(Skill(**skill_data))
            else:
                missing.append(Skill(**skill_data))

        return matched, missing

    def calculate_readiness(self, matched: int, total: int) -> int:
        if total == 0:
            return 0
        return round((matched / total) * 100)

    def get_skill_gap_summary(self, assessment: Assessment) -> dict:
        return {
            "career": assessment.target_career.title,
            "total_required": len(assessment.target_career.required_skills),
            "matched_count": len(assessment.matched_skills),
            "missing_count": len(assessment.missing_skills),
            "readiness_score": assessment.readiness_score,
            "missing_skills": [
                {
                    "name": s.name,
                    "category": s.category,
                    "difficulty": s.difficulty,
                    "estimated_hours": s.estimated_hours,
                }
                for s in assessment.missing_skills
            ],
        }
