import json

class ContextBuilder:
    """Builds a structured context string from user state models."""
    
    @staticmethod
    def build_user_context(
        target_role: str,
        readiness_score: int,
        known_skills: list[str],
        missing_skills: list[str],
        projects: list[str] = None,
        roadmap_progress: str = ""
    ) -> str:
        context = {
            "target_role": target_role,
            "career_readiness": f"{readiness_score}%",
            "known_skills": known_skills,
            "skills_to_learn": missing_skills,
        }
        if projects:
            context["projects"] = projects
        if roadmap_progress:
            context["roadmap_progress"] = roadmap_progress
            
        return json.dumps(context, indent=2)
