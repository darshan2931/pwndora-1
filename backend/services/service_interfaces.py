from app.domain.models import Skill, Career, UserProfile, Assessment, Roadmap, Project


class ResumeService:
    def parse(self, file_path: str) -> UserProfile:
        pass

    def extract_skills(self, text: str) -> list:
        pass


class CareerService:
    def analyze(self, profile: UserProfile, target: Career) -> Assessment:
        pass

    def calculate_readiness(self, matched: int, total: int) -> int:
        if total == 0:
            return 0
        return round((matched / total) * 100)


class RoadmapService:
    def generate(self, missing_skills: list, weekly_hours: int) -> Roadmap:
        pass

    def order_by_prerequisites(self, skills: list) -> list:
        pass


class RecommendationService:
    def recommend_projects(self, skills: list) -> list[Project]:
        pass

    def recommend_certifications(self, career: Career) -> list[str]:
        pass
