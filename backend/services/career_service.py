import logging
from typing import Dict, List, Tuple

from app.domain.models import Assessment, Career, Skill, CyberProfile
from knowledge.loader import knowledge_loader
from services.service_interfaces import CareerService as ICareerService

logger = logging.getLogger(__name__)


class CareerService(ICareerService):
    def __init__(self):
        self.kb = knowledge_loader

    def analyze(self, profile: CyberProfile, career_goal: str) -> Assessment:
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

        matched, missing = self._match_skills(profile.skills, career)
        readiness = self.calculate_readiness(profile, career, len(matched), len(career.required_skills + career.optional_skills))

        return Assessment(
            cyber_profile=profile,
            target_career=career,
            matched_skills=matched,
            missing_skills=missing,
            readiness_score=readiness,
        )

    def _match_skills(
        self, user_skills: List[Skill], career: Career
    ) -> Tuple[List[Skill], List[Skill]]:
        all_required = career.required_skills + career.optional_skills
        user_skills_lower = [s.name.lower() for s in user_skills]

        matched = []
        missing = []

        for skill_name in all_required:
            skill_data = self.kb.get_skill(skill_name) or {
                "name": skill_name,
                "category": "",
                "difficulty": "intermediate",
            }
            skill_data = dict(skill_data)
            if "unlocks" not in skill_data:
                skill_data["unlocks"] = []
            
            skill_obj = Skill(**skill_data)
            
            if skill_name.lower() in user_skills_lower:
                matched.append(skill_obj)
            else:
                missing.append(skill_obj)

        return matched, missing

    def calculate_readiness(self, profile: CyberProfile, career: Career, matched: int, total_skills: int) -> int:
        """
        Deterministic Readiness Engine
        Skills (42%)
        Projects (25%)
        Certifications (10%)
        Labs/Practice (15%)
        Consistency/Streak (8%)
        """
        if total_skills == 0:
            return 0
            
        skills_score = (matched / total_skills) * 42

        # Projects Score (max 25)
        # Assuming ~3 relevant projects means full score
        projects_count = len(profile.projects_completed)
        projects_score = min(25, (projects_count / 3.0) * 25)
        
        # Certifications Score (max 10)
        # Assuming 1 relevant cert is full score
        certs_count = len(profile.certifications)
        certs_score = min(10, certs_count * 10)
        
        # Labs (max 15)
        # Assuming 20 labs is full score
        labs_score = min(15, (profile.labs_completed / 20.0) * 15)
        
        # Consistency (max 8)
        # Assuming 14 day streak is full score
        streak_score = min(8, (profile.streak_days / 14.0) * 8)
        
        total_readiness = skills_score + projects_score + certs_score + labs_score + streak_score
        return int(round(total_readiness))

    def get_skill_dependency_graph(self, target_career: str) -> Dict[str, List[str]]:
        """
        Returns an adjacency list mapping skills to their required prerequisites
        for a specific career path.
        """
        role_data = self.kb.get_role(target_career)
        if not role_data:
            return {}
            
        required_skills = role_data.get("required_skills", [])
        graph = {}
        
        # We need to explore prerequisites recursively
        visited = set()
        queue = list(required_skills)
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            skill_data = self.kb.get_skill(current)
            if skill_data:
                prereqs = skill_data.get("prerequisites", [])
                graph[current] = prereqs
                queue.extend(prereqs)
            else:
                graph[current] = []
                
        return graph

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
