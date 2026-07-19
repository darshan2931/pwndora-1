import logging
from typing import List

from app.domain.models import CyberProfile
from services.career_service import CareerService
from knowledge.loader import knowledge_loader

logger = logging.getLogger(__name__)

class ProgressService:
    """Manages the user's progress and achievements deterministically."""
    
    def __init__(self):
        self.career_service = CareerService()
        self.kb = knowledge_loader
        
    def complete_skill(self, profile: CyberProfile, skill_name: str, target_career: str) -> dict:
        """Marks a skill as complete and recalculates readiness."""
        skill_data = self.kb.get_skill(skill_name)
        if not skill_data:
            raise ValueError(f"Unknown skill: {skill_name}")
            
        # Add to known skills if not already there
        known_names = [s.name.lower() for s in profile.skills]
        if skill_name.lower() not in known_names:
            from app.domain.models import Skill
            profile.skills.append(Skill(**skill_data))
            
        return self._recalculate_and_check_achievements(profile, target_career)
        
    def complete_project(self, profile: CyberProfile, project_title: str, target_career: str) -> dict:
        """Marks a project as complete and recalculates readiness."""
        if project_title not in profile.projects_completed:
            profile.projects_completed.append(project_title)
            
        return self._recalculate_and_check_achievements(profile, target_career)
        
    def add_study_hours(self, profile: CyberProfile, hours: int, target_career: str) -> dict:
        """Records study time and potentially increments streak."""
        # Simple simulation for now
        profile.labs_completed += max(1, hours // 2)
        profile.streak_days = min(profile.streak_days + 1, 30)
        
        return self._recalculate_and_check_achievements(profile, target_career)

    def _recalculate_and_check_achievements(self, profile: CyberProfile, target_career: str) -> dict:
        """Recalculates the readiness score and unlocks any new achievements."""
        assessment = self.career_service.analyze(profile, target_career)
        
        new_achievements = self._check_achievements(profile)
        for ach in new_achievements:
            if ach not in profile.achievements:
                profile.achievements.append(ach)
                
        return {
            "readiness_score": assessment.readiness_score,
            "matched_skills_count": len(assessment.matched_skills),
            "new_achievements": new_achievements,
            "profile": profile
        }

    def _check_achievements(self, profile: CyberProfile) -> List[str]:
        """Deterministic achievement unlocking."""
        unlocked = []
        
        if len(profile.skills) >= 1:
            unlocked.append("First Skill Learned")
        if len(profile.skills) >= 10:
            unlocked.append("Apprentice")
            
        if profile.streak_days >= 7:
            unlocked.append("7-Day Streak")
            
        if len(profile.projects_completed) >= 1:
            unlocked.append("First Project")
            
        return unlocked
