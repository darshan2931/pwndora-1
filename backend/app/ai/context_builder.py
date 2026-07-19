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

    @staticmethod
    def build_mentor_context(user, assessment, roadmap=None) -> str:
        context = {
            "user_name": getattr(user, "name", "User"),
            "target_role": str(assessment.career_goal) if assessment else "Unknown",
            "career_readiness": f"{assessment.readiness_score}%" if assessment else "0%",
            "known_skills": [str(s) for s in (assessment.matched_skills or [])] if assessment else [],
            "skills_to_learn": [str(s) for s in (assessment.missing_skills or [])] if assessment else [],
            "weekly_hours": getattr(assessment, "weekly_hours", 10) if assessment else 10,
        }
        if roadmap:
            steps = roadmap.steps or []
            completed = sum(1 for s in steps if s.get("status") == "completed")
            context["roadmap_progress"] = f"{completed}/{len(steps)} steps completed"
            context["estimated_weeks"] = getattr(roadmap, "estimated_weeks", 0)
        
        return json.dumps(context, indent=2)
