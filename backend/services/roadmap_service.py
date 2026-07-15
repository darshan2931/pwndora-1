import logging
from typing import List

from app.domain.models import Assessment, Roadmap, RoadmapStep, Skill
from knowledge.loader import knowledge_loader
from services.service_interfaces import RoadmapService as IRoadmapService

logger = logging.getLogger(__name__)


class RoadmapService(IRoadmapService):
    def __init__(self):
        self.kb = knowledge_loader

    def generate(self, assessment: Assessment, study_hours: int = 10) -> Roadmap:
        ordered_skills = self.order_by_prerequisites(assessment.missing_skills)
        steps = self._build_steps(ordered_skills)
        total_hours = sum(s.estimated_hours for s in steps)
        estimated_weeks = self._estimate_weeks(total_hours, study_hours)

        return Roadmap(
            steps=steps,
            total_hours=total_hours,
            estimated_weeks=estimated_weeks,
        )

    def order_by_prerequisites(self, skills: List[Skill]) -> List[Skill]:
        skill_map = {s.name.lower(): s for s in skills}
        in_degree = {s.name.lower(): 0 for s in skills}
        adj: dict[str, list[str]] = {s.name.lower(): [] for s in skills}

        for skill in skills:
            prereqs = self.kb.get_skill_prerequisites(skill.name)
            for prereq in prereqs:
                prereq_lower = prereq.lower()
                if prereq_lower in skill_map:
                    adj[prereq_lower].append(skill.name.lower())
                    in_degree[skill.name.lower()] += 1

        queue = [name for name, deg in in_degree.items() if deg == 0]
        ordered = []

        while queue:
            queue.sort()
            node = queue.pop(0)
            ordered.append(skill_map[node])
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordered) < len(skills):
            seen = {s.name.lower() for s in ordered}
            for skill in skills:
                if skill.name.lower() not in seen:
                    ordered.append(skill)

        return ordered

    def _build_steps(self, ordered_skills: List[Skill]) -> List[RoadmapStep]:
        steps = []
        for i, skill in enumerate(ordered_skills, 1):
            skill_data = self.kb.get_skill(skill.name) or {}
            steps.append(RoadmapStep(
                step=i,
                skill=skill,
                prerequisites=skill_data.get("prerequisites", []),
                estimated_hours=skill_data.get("estimated_hours", 10),
                resources=skill_data.get("learning_resources", []),
            ))
        return steps

    def _estimate_weeks(self, total_hours: int, study_hours: int) -> int:
        if study_hours <= 0:
            return max(1, total_hours // 10)
        return max(1, total_hours // study_hours)

    def get_roadmap_summary(self, roadmap: Roadmap) -> dict:
        return {
            "total_steps": len(roadmap.steps),
            "total_hours": roadmap.total_hours,
            "estimated_weeks": roadmap.estimated_weeks,
            "skills": [
                {
                    "step": step.step,
                    "name": step.skill.name,
                    "category": step.skill.category,
                    "difficulty": step.skill.difficulty,
                    "hours": step.estimated_hours,
                }
                for step in roadmap.steps
            ],
        }
