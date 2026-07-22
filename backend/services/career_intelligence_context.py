import logging
from typing import Optional

from database.session import SessionLocal
from models.sqlalchemy_models import (
    SkillEvidence, CareerRoleAnalysis, Roadmap, CareerChangeLog,
    ChatMemory, GitHubProfile, GitHubRepositoryEvidence, ResumeProfile,
    Assessment,
)

logger = logging.getLogger(__name__)


class CareerIntelligenceContextBuilder:
    def build_full_context(self, user_id: str) -> dict:
        context: dict = {
            "user": {"name": "", "target_role": "", "weekly_hours": 10},
            "readiness": {"score": 0, "level": "not_started"},
            "strengths": [],
            "developing": [],
            "weak_skills": [],
            "priority_gaps": [],
            "next_best_skill": None,
            "roadmap": {"total_steps": 0, "completed_steps": 0, "current_step": "", "estimated_weeks": 0, "phases": []},
            "recent_changes": [],
            "evidence_summary": {"resume": False, "github_repos": 0, "total_evidence_items": 0},
            "conversation_memory": {"summary": "", "important_facts": [], "next_goal": ""},
            "github": {"username": "", "repositories_count": 0, "top_languages": []},
        }

        try:
            context["user"] = self._load_user_info(user_id) or context["user"]
        except Exception as e:
            logger.warning("Failed to load user info: %s", e)

        try:
            evidence_list = self._load_skill_evidence(user_id)
            for ev in evidence_list:
                conf = ev.get("confidence", 0)
                entry = {"skill": ev["skill_name"], "confidence": conf, "evidence_sources": ev.get("sources", [])}
                if conf >= 70:
                    context["strengths"].append(entry)
                elif conf >= 40:
                    context["developing"].append(entry)
                else:
                    context["weak_skills"].append(entry)
            context["evidence_summary"]["total_evidence_items"] = len(evidence_list)
        except Exception as e:
            logger.warning("Failed to load skill evidence: %s", e)

        try:
            role_analysis = self._load_role_analysis(user_id)
            if role_analysis:
                context["readiness"] = {
                    "score": role_analysis.get("readiness_score", 0),
                    "level": role_analysis.get("readiness_level", "not_started"),
                }
                context["priority_gaps"] = role_analysis.get("skill_gaps", [])
                next_skill = role_analysis.get("recommended_next_skill")
                if next_skill:
                    context["next_best_skill"] = next_skill.get("skill_name") if isinstance(next_skill, dict) else str(next_skill)
        except Exception as e:
            logger.warning("Failed to load role analysis: %s", e)

        try:
            roadmap_data = self._load_roadmap(user_id)
            if roadmap_data:
                steps = roadmap_data.get("steps", [])
                completed = sum(1 for s in steps if s.get("status") == "completed")
                current = next((s for s in steps if s.get("status") in ("in-progress", "available")), None)
                context["roadmap"] = {
                    "total_steps": len(steps),
                    "completed_steps": completed,
                    "current_step": current.get("title", "") if current else "",
                    "estimated_weeks": roadmap_data.get("estimated_weeks", 0),
                    "phases": roadmap_data.get("phases", []),
                }
        except Exception as e:
            logger.warning("Failed to load roadmap: %s", e)

        try:
            context["recent_changes"] = self._load_recent_changes(user_id)
        except Exception as e:
            logger.warning("Failed to load recent changes: %s", e)

        try:
            context["conversation_memory"] = self._load_conversation_memory(user_id)
        except Exception as e:
            logger.warning("Failed to load conversation memory: %s", e)

        try:
            github_data = self._load_github_data(user_id)
            if github_data:
                context["github"] = github_data
                context["evidence_summary"]["github_repos"] = github_data.get("repositories_count", 0)
        except Exception as e:
            logger.warning("Failed to load GitHub data: %s", e)

        try:
            context["evidence_summary"]["resume"] = self._has_resume(user_id)
        except Exception as e:
            logger.warning("Failed to check resume: %s", e)

        return context

    def build_context_for_question(self, user_id: str, question: str) -> dict:
        full = self.build_full_context(user_id)
        intent = self._detect_question_intent(question)
        return self._select_relevant_context(full, intent, question)

    def build_daily_briefing_context(self, user_id: str) -> dict:
        full = self.build_full_context(user_id)
        return self._select_relevant_context(full, "progress", "")

    def build_roadmap_explanation_context(self, user_id: str) -> dict:
        full = self.build_full_context(user_id)
        return self._select_relevant_context(full, "roadmap", "")

    def build_skill_explanation_context(self, user_id: str, skill_id: str) -> dict:
        full = self.build_full_context(user_id)
        return self._select_relevant_context(full, "skill", skill_id)

    def build_project_mentor_context(self, user_id: str, project_info: dict) -> dict:
        full = self.build_full_context(user_id)
        ctx = self._select_relevant_context(full, "project", "")
        ctx["project_info"] = project_info
        return ctx

    def build_interview_prep_context(self, user_id: str) -> dict:
        full = self.build_full_context(user_id)
        return self._select_relevant_context(full, "interview", "")

    # ── Private helpers ────────────────────────────────────────────────

    def _load_user_info(self, user_id: str) -> Optional[dict]:
        db = SessionLocal()
        try:
            from models.sqlalchemy_models import User
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            assessment = db.query(Assessment).filter(Assessment.user_id == user_id).order_by(Assessment.created_at.desc()).first()
            return {
                "name": user.name or "",
                "target_role": str(assessment.career_goal) if assessment else "",
                "weekly_hours": assessment.weekly_hours if assessment else 10,
            }
        finally:
            db.close()

    def _load_skill_evidence(self, user_id: str) -> list:
        db = SessionLocal()
        try:
            items = db.query(SkillEvidence).filter(SkillEvidence.user_id == user_id).all()
            return [
                {
                    "skill_name": e.skill_name,
                    "skill_id": e.skill_id,
                    "category": e.category,
                    "confidence": e.confidence,
                    "confidence_level": e.confidence_level,
                    "sources": e.sources or [],
                    "evidence_count": e.evidence_count,
                }
                for e in items
            ]
        finally:
            db.close()

    def _load_role_analysis(self, user_id: str) -> Optional[dict]:
        db = SessionLocal()
        try:
            analysis = db.query(CareerRoleAnalysis).filter(CareerRoleAnalysis.user_id == user_id).order_by(CareerRoleAnalysis.created_at.desc()).first()
            if not analysis:
                return None
            return {
                "role_id": analysis.role_id,
                "role_name": analysis.role_name,
                "readiness_score": analysis.readiness_score,
                "readiness_level": analysis.readiness_level,
                "total_skills": analysis.total_skills,
                "covered_count": analysis.covered_count,
                "missing_count": analysis.missing_count,
                "skill_gaps": analysis.skill_gaps or [],
                "recommended_next_skill": analysis.recommended_next_skill,
                "learning_path": analysis.learning_path or [],
            }
        finally:
            db.close()

    def _load_roadmap(self, user_id: str) -> Optional[dict]:
        db = SessionLocal()
        try:
            roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id).order_by(Roadmap.created_at.desc()).first()
            if not roadmap:
                return None
            return {
                "id": str(roadmap.id),
                "steps": roadmap.steps or [],
                "phases": roadmap.phases or [],
                "total_hours": roadmap.total_hours,
                "estimated_weeks": roadmap.estimated_weeks,
                "readiness_score_at_creation": roadmap.readiness_score_at_creation,
            }
        finally:
            db.close()

    def _load_recent_changes(self, user_id: str) -> list:
        db = SessionLocal()
        try:
            changes = db.query(CareerChangeLog).filter(CareerChangeLog.user_id == user_id).order_by(CareerChangeLog.created_at.desc()).limit(10).all()
            return [
                {
                    "skill": c.skill_name or "",
                    "old_confidence": c.old_value if isinstance(c.old_value, (int, float)) else 0,
                    "new_confidence": c.new_value if isinstance(c.new_value, (int, float)) else 0,
                    "change_type": c.change_type,
                    "explanation": c.explanation or "",
                    "created_at": str(c.created_at) if c.created_at else "",
                }
                for c in changes
            ]
        finally:
            db.close()

    def _load_conversation_memory(self, user_id: str) -> dict:
        db = SessionLocal()
        try:
            memory = db.query(ChatMemory).filter(ChatMemory.user_id == user_id).order_by(ChatMemory.created_at.desc()).first()
            if not memory:
                return {"summary": "", "important_facts": [], "next_goal": ""}
            return {
                "summary": memory.summary or "",
                "important_facts": memory.important_facts or [],
                "next_goal": memory.next_goal or "",
            }
        finally:
            db.close()

    def _load_github_data(self, user_id: str) -> Optional[dict]:
        db = SessionLocal()
        try:
            profile = db.query(GitHubProfile).filter(GitHubProfile.user_id == user_id).order_by(GitHubProfile.created_at.desc()).first()
            if not profile:
                return None
            repos = db.query(GitHubRepositoryEvidence).filter(GitHubRepositoryEvidence.github_profile_id == str(profile.id)).all()
            all_langs: dict = {}
            for r in repos:
                if r.languages:
                    for lang, bytes_val in r.languages.items():
                        all_langs[lang] = all_langs.get(lang, 0) + (bytes_val if isinstance(bytes_val, (int, float)) else 0)
            top_langs = sorted(all_langs.keys(), key=lambda k: all_langs[k], reverse=True)[:5]
            return {
                "username": profile.username or "",
                "repositories_count": len(repos),
                "top_languages": top_langs,
                "public_repositories": profile.public_repositories or 0,
                "followers": profile.followers or 0,
            }
        finally:
            db.close()

    def _has_resume(self, user_id: str) -> bool:
        db = SessionLocal()
        try:
            profile = db.query(ResumeProfile).filter(ResumeProfile.user_id == user_id).first()
            return profile is not None
        finally:
            db.close()

    def _detect_question_intent(self, question: str) -> str:
        q = question.lower()
        if any(kw in q for kw in ["career", "path", "what should i", "recommend", "next skill", "blocked", "readiness"]):
            return "career"
        if any(kw in q for kw in ["roadmap", "order", "sequence", "why this", "next step", "phase"]):
            return "roadmap"
        if any(kw in q for kw in ["project", "build", "implement", "architecture", "design"]):
            return "project"
        if any(kw in q for kw in ["interview", "hiring", "job", "resume tip", "portfolio", "salary"]):
            return "interview"
        if any(kw in q for kw in ["progress", "improve", "changed", "what did i", "recent", "update"]):
            return "progress"
        if any(kw in q for kw in ["teach", "explain", "what is", "how does", "learn", "tutorial"]):
            return "skill"
        return "general"

    def _select_relevant_context(self, full: dict, intent: str, extra: str) -> dict:
        keys_by_intent = {
            "career": {"user", "readiness", "strengths", "weak_skills", "priority_gaps", "next_best_skill", "evidence_summary"},
            "roadmap": {"user", "roadmap", "readiness", "strengths", "developing"},
            "project": {"user", "roadmap", "evidence_summary", "github"},
            "interview": {"user", "strengths", "developing", "weak_skills", "evidence_summary", "github"},
            "progress": {"user", "recent_changes", "readiness", "evidence_summary"},
            "skill": {"user", "readiness", "strengths", "developing", "weak_skills"},
            "general": set(full.keys()),
        }
        allowed = keys_by_intent.get(intent, set(full.keys()))
        result = {k: v for k, v in full.items() if k in allowed}
        if intent == "skill" and extra:
            result["skill_focus"] = extra
        return result
