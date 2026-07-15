from typing import List

from app.domain.models import Skill, Career, UserProfile, Assessment, Roadmap, Project


class ResumeService:
    def parse(self, file_path: str) -> UserProfile:
        pass

    def extract_skills(self, text: str) -> list:
        pass


class CareerService:
    def analyze(self, user_skills: list[str], career_goal: str) -> Assessment:
        pass

    def calculate_readiness(self, matched: int, total: int) -> int:
        if total == 0:
            return 0
        return round((matched / total) * 100)


class RoadmapService:
    def generate(self, assessment: Assessment, study_hours: int = 10) -> Roadmap:
        pass

    def order_by_prerequisites(self, skills: list) -> list:
        pass


class RecommendationService:
    def recommend_projects(self, assessment: Assessment, max_projects: int = 5) -> List[dict]:
        pass

    def recommend_certifications(self, assessment: Assessment) -> List[dict]:
        pass
