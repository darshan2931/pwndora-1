import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.career_service import CareerService
from services.recommendation_service import RecommendationService


@pytest.fixture
def recommendation_service():
    return RecommendationService()


@pytest.fixture
def career_service():
    return CareerService()


@pytest.fixture
def sample_assessment(career_service):
    return career_service.analyze(
        user_skills=["Linux"],
        career_goal="SOC Analyst",
    )


class TestRecommendationService:
    def test_recommend_projects_returns_list(self, recommendation_service, sample_assessment):
        projects = recommendation_service.recommend_projects(sample_assessment)
        assert isinstance(projects, list)
        assert len(projects) > 0

    def test_recommend_projects_max_limit(self, recommendation_service, sample_assessment):
        projects = recommendation_service.recommend_projects(sample_assessment, max_projects=2)
        assert len(projects) <= 2

    def test_recommend_projects_have_required_fields(self, recommendation_service, sample_assessment):
        projects = recommendation_service.recommend_projects(sample_assessment)
        for p in projects:
            assert "title" in p
            assert "difficulty" in p
            assert "skills" in p
            assert "estimated_hours" in p

    def test_recommend_certifications_returns_list(self, recommendation_service, sample_assessment):
        certs = recommendation_service.recommend_certifications(sample_assessment)
        assert isinstance(certs, list)
        assert len(certs) > 0

    def test_recommend_certifications_have_required_fields(self, recommendation_service, sample_assessment):
        certs = recommendation_service.recommend_certifications(sample_assessment)
        for c in certs:
            assert "name" in c
            assert "vendor" in c
            assert "difficulty" in c

    def test_get_all_recommendations(self, recommendation_service, sample_assessment):
        result = recommendation_service.get_all_recommendations(sample_assessment)
        assert "career" in result
        assert "projects" in result
        assert "certifications" in result
        assert "suggested_projects" in result

    def test_recommendations_for_unknown_career(self, career_service, recommendation_service):
        assessment = career_service.analyze(
            user_skills=[],
            career_goal="Unknown Career",
        )
        projects = recommendation_service.recommend_projects(assessment)
        certs = recommendation_service.recommend_certifications(assessment)
        assert isinstance(projects, list)
        assert isinstance(certs, list)
