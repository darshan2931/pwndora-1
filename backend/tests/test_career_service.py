import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.models import Assessment, Skill
from services.career_service import CareerService


@pytest.fixture
def career_service():
    return CareerService()


class TestCareerService:
    def test_analyze_known_career(self, career_service):
        assessment = career_service.analyze(
            user_skills=["Linux", "Python", "SIEM"],
            career_goal="SOC Analyst",
        )
        assert isinstance(assessment, Assessment)
        assert assessment.target_career.title == "SOC Analyst"
        assert assessment.readiness_score > 0

    def test_analyze_unknown_career(self, career_service):
        assessment = career_service.analyze(
            user_skills=["Linux"],
            career_goal="Unknown Career",
        )
        assert isinstance(assessment, Assessment)
        assert assessment.target_career.title == "Unknown Career"
        assert assessment.readiness_score == 0

    def test_analyze_with_all_skills(self, career_service):
        role = career_service.kb.get_role("SOC Analyst")
        all_skills = role["required_skills"] + role.get("optional_skills", [])
        assessment = career_service.analyze(
            user_skills=all_skills,
            career_goal="SOC Analyst",
        )
        assert assessment.readiness_score == 100
        assert len(assessment.missing_skills) == 0

    def test_analyze_with_no_skills(self, career_service):
        assessment = career_service.analyze(
            user_skills=[],
            career_goal="SOC Analyst",
        )
        assert assessment.readiness_score == 0
        assert len(assessment.matched_skills) == 0
        assert len(assessment.missing_skills) > 0

    def test_calculate_readiness(self, career_service):
        assert career_service.calculate_readiness(5, 10) == 50
        assert career_service.calculate_readiness(0, 10) == 0
        assert career_service.calculate_readiness(10, 10) == 100
        assert career_service.calculate_readiness(0, 0) == 0

    def test_match_skills_returns_tuple(self, career_service):
        career = career_service.kb.get_role("SOC Analyst")
        from app.domain.models import Career
        career_obj = Career(
            id="soc-analyst",
            title="SOC Analyst",
            description="",
            required_skills=career["required_skills"],
            optional_skills=career.get("optional_skills", []),
        )
        matched, missing = career_service._match_skills(["Linux", "Python"], career_obj)
        assert isinstance(matched, list)
        assert isinstance(missing, list)

    def test_skill_gap_summary(self, career_service):
        assessment = career_service.analyze(
            user_skills=["Linux"],
            career_goal="SOC Analyst",
        )
        summary = career_service.get_skill_gap_summary(assessment)
        assert "career" in summary
        assert "total_required" in summary
        assert "matched_count" in summary
        assert "missing_count" in summary
        assert "readiness_score" in summary
