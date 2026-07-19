from typing import List

from app.domain.models import CyberProfile, Assessment, Roadmap


class ResumeService:
    def parse(self, file_path: str) -> CyberProfile:
        raise NotImplementedError()

    def extract_skills(self, text: str) -> list:
        raise NotImplementedError()


class CareerService:
    def analyze(self, user_skills: list[str], career_goal: str) -> Assessment:
        raise NotImplementedError()

    def calculate_readiness(self, matched: int, total: int) -> int:
        if total == 0:
            return 0
        return round((matched / total) * 100)


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
