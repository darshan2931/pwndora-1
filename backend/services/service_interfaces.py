from typing import List

from app.domain.models import CyberProfile, Assessment, Roadmap


class ResumeService:
    def parse(self, file_path: str) -> CyberProfile:
        raise NotImplementedError()

    def extract_skills(self, text: str) -> list:
        raise NotImplementedError()


class CareerService:
    def analyze(self, profile: CyberProfile, career_goal: str) -> Assessment:
        raise NotImplementedError()

    def calculate_readiness(self, profile: CyberProfile, career: any, matched: int, total_skills: int) -> int:
        if total_skills == 0:
            return 0
        return round((matched / total_skills) * 100)


class RoadmapService:
    def generate(self, assessment: Assessment, study_hours: int = 10) -> Roadmap:
        raise NotImplementedError()

    def order_by_prerequisites(self, skills: list) -> list:
        raise NotImplementedError()


class RecommendationService:
    def recommend_projects(self, assessment: Assessment, max_projects: int = 5) -> List[dict]:
        raise NotImplementedError()

    def recommend_certifications(self, assessment: Assessment) -> List[dict]:
        raise NotImplementedError()
