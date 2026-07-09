from domain.models import UserProfile, Career, Assessment, Roadmap
from services.service_interfaces import ResumeService, CareerService, RoadmapService


class CareerOrchestrator:
    def __init__(
        self,
        resume_svc: ResumeService,
        career_svc: CareerService,
        roadmap_svc: RoadmapService,
    ):
        self.resume_svc = resume_svc
        self.career_svc = career_svc
        self.roadmap_svc = roadmap_svc

    def analyze(self, resume_file: str = None, manual_skills: list = None, career_goal: str = None, weekly_hours: int = 10):
        profile = UserProfile()

        if resume_file:
            profile = self.resume_svc.parse(resume_file)
        elif manual_skills:
            profile.skills = [Skill(name=s, category="", difficulty="") for s in manual_skills]

        career = Career(id=career_goal, title=career_goal, description="", required_skills=[])
        assessment = self.career_svc.analyze(profile, career)
        roadmap = self.roadmap_svc.generate(assessment.missing_skills, weekly_hours)

        return assessment, roadmap
