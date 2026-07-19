import logging
from typing import Tuple

from app.domain.models import Assessment, Roadmap
from knowledge.loader import knowledge_loader
from services.career_service import CareerService
from services.roadmap_service import RoadmapService
from services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)


class CareerOrchestrator:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.kb = knowledge_loader
        self.career_service = CareerService()
        self.roadmap_service = RoadmapService()
        self.recommendation_service = RecommendationService()

    def analyze(
        self,
        user_skills: list[str],
        career_goal: str,
        study_hours: int = 10,
    ) -> Tuple[Assessment, Roadmap]:
        from app.domain.models import CyberProfile, Skill
        skills = [Skill(name=s, category="", difficulty="beginner") for s in user_skills]
        profile = CyberProfile(skills=skills)
        assessment = self.career_service.analyze(profile, career_goal)
        roadmap = self.roadmap_service.generate(assessment, study_hours)
        return assessment, roadmap

    def _profile_from_user_skills(self, user_skills: list[str]):
        from app.domain.models import CyberProfile, Skill
        skills = [Skill(name=s, category="", difficulty="beginner") for s in user_skills]
        return CyberProfile(skills=skills)

    async def analyze_with_ai(
        self,
        user_skills: list[str],
        career_goal: str,
        study_hours: int = 10,
    ) -> dict:
        assessment, roadmap = self.analyze(user_skills, career_goal, study_hours)

        ai_summary = ""
        confidence = 1.0

        if self.ai_service:
            try:
                ai_summary = await self.ai_service.explain_career(context_data={
                    "target_role": career_goal,
                    "readiness_score": assessment.readiness_score,
                    "known_skills": [s.name for s in assessment.matched_skills],
                    "missing_skills": [s.name for s in assessment.missing_skills],
                })
                confidence = 0.8
            except Exception as e:
                logger.warning("AI roadmap explanation failed: %s", e)
                ai_summary = f"Your readiness for {career_goal} is {assessment.readiness_score}%."
                confidence = 0.5

        rec = self.recommendation_service.get_next_recommendation(
            self._profile_from_user_skills(user_skills), career_goal
        )
        projects = []
        if rec.next_project:
            projects.append(rec.next_project)

        return {
            "career_goal": career_goal,
            "career_readiness": assessment.readiness_score,
            "matched_skills": [s.name for s in assessment.matched_skills],
            "missing_skills": [s.name for s in assessment.missing_skills],
            "roadmap": [
                {
                    "step": step.step,
                    "skill": step.skill.name,
                    "prerequisites": step.prerequisites,
                    "estimated_hours": step.estimated_hours,
                    "resources": step.resources,
                }
                for step in roadmap.steps
            ],
            "recommended_projects": projects,
            "estimated_weeks": roadmap.estimated_weeks,
            "ai_summary": ai_summary,
            "confidence": confidence,
        }
