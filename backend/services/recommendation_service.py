import logging
from typing import List

from app.domain.models import Assessment, Career, Project
from knowledge.loader import knowledge_loader
from services.service_interfaces import RecommendationService as IRecommendationService

logger = logging.getLogger(__name__)


class RecommendationService(IRecommendationService):
    def __init__(self):
        self.kb = knowledge_loader

    def recommend_projects(self, assessment: Assessment, max_projects: int = 5) -> List[dict]:
        all_projects = self.kb.get_projects()
        missing_skill_names = {s.name.lower() for s in assessment.missing_skills}
        matched_skill_names = {s.name.lower() for s in assessment.matched_skills}

        scored_projects = []
        for project in all_projects:
            project_skills = {s.lower() for s in project.get("skills", [])}
            relevance = len(project_skills & missing_skill_names)
            leverage = len(project_skills & matched_skill_names)
            score = relevance * 2 + leverage

            if score > 0:
                scored_projects.append((score, project))

        scored_projects.sort(key=lambda x: (-x[0], x[1].get("estimated_hours", 0)))

        recommended = []
        for _, project in scored_projects[:max_projects]:
            recommended.append({
                "title": project["title"],
                "difficulty": project["difficulty"],
                "skills": project["skills"],
                "estimated_hours": project.get("estimated_hours", 0),
                "github_deliverables": project.get("github_deliverables", []),
            })

        return recommended

    def recommend_certifications(self, assessment: Assessment) -> List[dict]:
        role_certs = self.kb.get_certifications_for_role(assessment.target_career.title)

        recommended = []
        for cert in role_certs:
            recommended.append({
                "name": cert["name"],
                "vendor": cert["vendor"],
                "difficulty": cert["difficulty"],
                "prerequisites": cert.get("prerequisites", []),
            })

        return recommended

    def get_all_recommendations(self, assessment: Assessment) -> dict:
        return {
            "career": assessment.target_career.title,
            "projects": self.recommend_projects(assessment),
            "certifications": self.recommend_certifications(assessment),
            "suggested_projects": assessment.target_career.suggested_projects,
        }
