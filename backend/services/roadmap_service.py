import logging
from typing import List, Optional

from app.domain.models import CyberProfile, Roadmap, RoadmapStep, Skill
from knowledge.loader import knowledge_loader
from services.career_service import CareerService

logger = logging.getLogger(__name__)


class RoadmapService:
    def __init__(self):
        self.kb = knowledge_loader
        self.career_service = CareerService()

    def generate_timeline(self, profile: CyberProfile, target_career: str, study_hours: int = 10) -> Roadmap:
        """
        Deterministically generates a roadmap based on the skill dependency graph.
        Groups skills into a logical learning sequence without hallucinating.
        """
        graph = self.career_service.get_skill_dependency_graph(target_career)
        known_skill_names = {s.name.lower() for s in profile.skills}
        
        # Topological sort to determine learning order
        # Since this is a learning graph, we want to start from nodes with 0 prereqs
        # and work our way up.
        
        in_degree = {node: 0 for node in graph.keys()}
        for node, prereqs in graph.items():
            for prereq in prereqs:
                if prereq in in_degree:
                    in_degree[node] += 1
                
        # We only want to schedule skills the user hasn't learned yet
        queue = [node for node in in_degree.keys() if in_degree[node] == 0]
        
        learning_sequence = []
        visited = set()
        
        # Simple BFS topological sort approximation
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
                
            visited.add(current)
            if current.lower() not in known_skill_names:
                learning_sequence.append(current)
                
            # Decrease in-degree for dependents
            for node, prereqs in graph.items():
                if current in prereqs:
                    in_degree[node] -= 1
                    if in_degree[node] == 0 and node not in visited:
                        queue.append(node)
                        
        # Construct Roadmap steps
        steps = []
        total_hours = 0
        
        for i, skill_name in enumerate(learning_sequence):
            skill_data = self.kb.get_skill(skill_name) or {
                "name": skill_name,
                "category": "General",
                "difficulty": "beginner",
                "estimated_hours": 10
            }
            
            hours = skill_data.get("estimated_hours", 10)
            total_hours += hours
            
            steps.append(
                RoadmapStep(
                    step=i + 1,
                    skill=Skill(**skill_data),
                    prerequisites=skill_data.get("prerequisites", []),
                    estimated_hours=hours,
                    resources=skill_data.get("learning_resources", []),
                )
            )
            
        estimated_weeks = max(1, total_hours // max(1, study_hours))
        
        return Roadmap(
            steps=steps,
            total_hours=total_hours,
            estimated_weeks=estimated_weeks
        )

    def generate(self, assessment, study_hours: int = 10):
        """Generate roadmap from domain Assessment model."""
        from app.domain.models import CyberProfile
        profile = CyberProfile(skills=list(assessment.matched_skills or []))
        target = str(assessment.target_career.title) if hasattr(assessment, 'target_career') else ""
        return self.generate_timeline(profile, target, study_hours)
