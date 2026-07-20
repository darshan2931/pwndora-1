import logging
from typing import Tuple

from app.domain.models import Assessment, Roadmap
from knowledge.loader import knowledge_loader
from services.career_service import CareerService
from services.roadmap_service import RoadmapService
from services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

RESOURCE_URLS = {
    "Microsoft Learn": {"url": "https://learn.microsoft.com/en-us/windows/", "type": "course"},
    "Splunk Free Training": {"url": "https://www.splunk.com/en_us/training/free-online-training.html", "type": "course"},
    "Splunk Documentation": {"url": "https://docs.splunk.com/", "type": "article"},
    "Wireshark Documentation": {"url": "https://www.wireshark.org/docs/", "type": "article"},
    "Wireshark Wiki": {"url": "https://wiki.wireshark.org/", "type": "article"},
    "Cisco Skills for All": {"url": "https://skillsforall.com/", "type": "course"},
    "TryHackMe": {"url": "https://tryhackme.com/", "type": "lab"},
    "Hack The Box": {"url": "https://www.hackthebox.com/", "type": "lab"},
    "SANS DFIR": {"url": "https://www.sans.org/white-papers/incident-handling-process/", "type": "article"},
    "Automate the Boring Stuff": {"url": "https://automatetheboringstuff.com/", "type": "book"},
    "MITRE ATT&CK Website": {"url": "https://attack.mitre.org/", "type": "article"},
    "The Linux Command Line": {"url": "https://linuxcommand.org/tlcl.php", "type": "book"},
    "OverTheWire": {"url": "https://overthewire.org/wargames/bandit/", "type": "lab"},
    "Nmap Documentation": {"url": "https://nmap.org/docs.html", "type": "article"},
    "PortSwigger Web Security Academy": {"url": "https://portswigger.net/web-security", "type": "course"},
    "PortSwigger": {"url": "https://portswigger.net/web-security", "type": "course"},
    "DFIR Training": {"url": "https://www.dfir.training/", "type": "course"},
    "Kubernetes Documentation": {"url": "https://kubernetes.io/docs/home/", "type": "article"},
    "HashiCorp Learn": {"url": "https://developer.hashicorp.com/terraform/tutorials", "type": "course"},
    "AWS Documentation": {"url": "https://docs.aws.amazon.com/iam/", "type": "article"},
    "OWASP": {"url": "https://owasp.org/www-project-top-ten/", "type": "article"},
    "Splunk": {"url": "https://www.splunk.com/en_us/training/free-online-training.html", "type": "course"},
    "Wireshark": {"url": "https://www.wireshark.org/docs/", "type": "article"},
}


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

        roadmap_nodes = []
        for i, step in enumerate(roadmap.steps):
            if i == 0:
                status = "in-progress"
            elif i == 1:
                status = "available"
            else:
                status = "locked"
            resources = []
            for j, r in enumerate(step.resources):
                if isinstance(r, str):
                    meta = RESOURCE_URLS.get(r, {})
                    resources.append({
                        "id": f"res-{i}-{j}",
                        "title": r,
                        "type": meta.get("type", "article"),
                        "url": meta.get("url", "#"),
                        "free": True,
                    })
                else:
                    resources.append(r)
            roadmap_nodes.append({
                "id": f"step-{i}",
                "title": step.skill.name,
                "description": f"Learn {step.skill.name} for {career_goal}",
                "type": "skill",
                "status": status,
                "estimatedHours": step.estimated_hours,
                "difficulty": step.skill.difficulty.capitalize() if step.skill.difficulty else "Beginner",
                "skills": [step.skill.name],
                "prerequisites": step.prerequisites,
                "resources": resources,
            })

        return {
            "career_goal": career_goal,
            "career_readiness": assessment.readiness_score,
            "matched_skills": [s.name for s in assessment.matched_skills],
            "missing_skills": [s.name for s in assessment.missing_skills],
            "roadmap": roadmap_nodes,
            "recommended_projects": projects,
            "estimated_weeks": roadmap.estimated_weeks,
            "ai_summary": ai_summary,
            "confidence": confidence,
        }
