import logging
from typing import Optional, Tuple

from app.domain.models import Assessment, Career, Project, Roadmap, RoadmapStep, Skill, UserProfile
from knowledge.loader import knowledge_loader

logger = logging.getLogger(__name__)


class CareerOrchestrator:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.kb = knowledge_loader

    def analyze(
        self,
        user_skills: list[str],
        career_goal: str,
        study_hours: int = 10,
    ) -> Tuple[Assessment, Roadmap]:
        role_data = self.kb.get_role(career_goal)
        if not role_data:
            role_data = {
                "role": career_goal,
                "required_skills": [],
                "optional_skills": [],
            }

        all_required = role_data.get("required_skills", []) + role_data.get("optional_skills", [])

        matched = []
        missing = []
        user_skills_lower = [s.lower() for s in user_skills]

        for skill_name in all_required:
            skill_data = self.kb.get_skill(skill_name) or {"name": skill_name, "category": "", "difficulty": "intermediate"}
            if skill_name.lower() in user_skills_lower:
                matched.append(Skill(**skill_data))
            else:
                missing.append(Skill(**skill_data))

        readiness = 0
        if len(all_required) > 0:
            readiness = int((len(matched) / len(all_required)) * 100)

        career = Career(
            id=career_goal.lower().replace(" ", "-"),
            title=career_goal,
            description=role_data.get("description", ""),
            required_skills=role_data.get("required_skills", []),
            optional_skills=role_data.get("optional_skills", []),
            recommended_certifications=role_data.get("recommended_certifications", []),
            suggested_projects=role_data.get("suggested_projects", []),
        )

        assessment = Assessment(
            user_profile=UserProfile(skills=[Skill(name=s, category="", difficulty="") for s in user_skills]),
            target_career=career,
            matched_skills=matched,
            missing_skills=missing,
            readiness_score=readiness,
        )

        roadmap = self._build_roadmap(missing, study_hours)

        return assessment, roadmap

    def _build_roadmap(self, missing_skills: list[Skill], study_hours: int) -> Roadmap:
        steps = []
        for i, skill in enumerate(missing_skills, 1):
            skill_data = self.kb.get_skill(skill.name) or {}
            steps.append(RoadmapStep(
                step=i,
                skill=skill,
                prerequisites=skill_data.get("prerequisites", []),
                estimated_hours=skill_data.get("estimated_hours", 10),
                resources=skill_data.get("learning_resources", []),
            ))

        total_hours = sum(s.estimated_hours for s in steps)
        estimated_weeks = max(1, total_hours // study_hours) if study_hours > 0 else total_hours // 10

        return Roadmap(steps=steps, total_hours=total_hours, estimated_weeks=estimated_weeks)

    async def analyze_with_ai(
        self,
        user_skills: list[str],
        career_goal: str,
        study_hours: int = 10,
    ) -> dict:
        assessment, roadmap = self.analyze(user_skills, career_goal, study_hours)

        ai_summary = ""
        confidence = 1.0
        ai_projects = []

        if self.ai_service:
            try:
                ai_summary, confidence = await self.ai_service.explain_roadmap(assessment, roadmap)
            except Exception as e:
                logger.warning("AI roadmap explanation failed: %s", e)
                ai_summary = f"Your readiness for {career_goal} is {assessment.readiness_score}%."
                confidence = 0.5

        projects_data = self.kb.get_projects()
        skill_names = [s.name for s in assessment.missing_skills]
        ai_projects = [
            p for p in projects_data
            if any(s in skill_names for s in p.get("skills", []))
        ][:5]

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
            "projects": ai_projects,
            "estimated_weeks": roadmap.estimated_weeks,
            "ai_summary": ai_summary,
            "confidence": confidence,
        }
