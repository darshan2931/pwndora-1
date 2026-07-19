import logging
from typing import Optional, List, Dict

from app.domain.models import CyberProfile, Recommendation
from knowledge.loader import knowledge_loader
from services.career_service import CareerService

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self):
        self.kb = knowledge_loader
        self.career_service = CareerService()

    def get_next_recommendation(self, profile: CyberProfile, target_career: str) -> Recommendation:
        """
        Deterministically finds the next best skill to learn based on the dependency graph.
        A skill is 'ready to learn' if all its prerequisites are in the user's known skills.
        """
        graph = self.career_service.get_skill_dependency_graph(target_career)
        
        known_skill_names = {s.name.lower() for s in profile.skills}
        
        # Traverse graph to find the first unlearned skill where all prereqs are met
        # We process in order of depth/dependencies (e.g. foundational skills first)
        
        # Sort graph by number of prerequisites to suggest fundamentals first
        sorted_skills = sorted(graph.items(), key=lambda x: len(x[1]))
        
        next_skill_name = None
        for skill_name, prereqs in sorted_skills:
            if skill_name.lower() in known_skill_names:
                continue
                
            # Check if all prereqs are met
            prereqs_met = all(p.lower() in known_skill_names for p in prereqs)
            
            if prereqs_met:
                next_skill_name = skill_name
                break
                
        if not next_skill_name:
            # All skills learned or no path found, suggest a project
            return self._recommend_project(profile, target_career)
            
        skill_data = self.kb.get_skill(next_skill_name)
        if not skill_data:
            return Recommendation(reason="Unknown skill in roadmap")
            
        # Find what this skill unlocks by checking what has it as a prerequisite
        unlocks = [s for s, p in graph.items() if next_skill_name in p]
        
        reason = "Required for your target role."
        if unlocks:
            reason = f"Required before {', '.join(unlocks[:2])}. Unlocks {len(unlocks)} advanced topics."
            
        return Recommendation(
            next_skill=skill_data.get("name"),
            reason=reason,
            estimated_hours=skill_data.get("estimated_hours", 10),
            difficulty=skill_data.get("difficulty", "beginner")
        )

    def _recommend_project(self, profile: CyberProfile, target_career: str) -> Recommendation:
        role_data = self.kb.get_role(target_career)
        if not role_data:
            return Recommendation(reason="You have mastered the skills. Keep practicing.")
            
        suggested_projects = role_data.get("suggested_projects", [])
        completed_lower = [p.lower() for p in profile.projects_completed]
        
        for proj_title in suggested_projects:
            if proj_title.lower() not in completed_lower:
                return Recommendation(
                    next_project=proj_title,
                    reason="Demonstrates your skills in a practical scenario for employers.",
                    estimated_hours=20,
                    difficulty="intermediate"
                )
                
        return Recommendation(
            reason="You are fully ready. Focus on interview prep.",
            difficulty="advanced"
        )
