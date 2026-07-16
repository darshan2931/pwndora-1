import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrators.career_orchestrator import CareerOrchestrator


@pytest.fixture
def orchestrator():
    return CareerOrchestrator(ai_service=None)


class TestCareerOrchestrator:
    def test_analyze_returns_assessment_and_roadmap(self, orchestrator):
        assessment, roadmap = orchestrator.analyze(
            user_skills=["Linux", "Python"],
            career_goal="SOC Analyst",
            study_hours=10,
        )
        assert assessment is not None
        assert roadmap is not None
        assert assessment.readiness_score > 0
        assert len(roadmap.steps) > 0

    def test_analyze_unknown_career(self, orchestrator):
        assessment, roadmap = orchestrator.analyze(
            user_skills=[],
            career_goal="Unknown",
            study_hours=10,
        )
        assert assessment.readiness_score == 0
        assert len(roadmap.steps) == 0

    def test_analyze_with_ai_returns_dict(self, orchestrator):
        import asyncio
        result = asyncio.run(
            orchestrator.analyze_with_ai(
                user_skills=["Linux", "SIEM"],
                career_goal="SOC Analyst",
                study_hours=10,
            )
        )
        assert isinstance(result, dict)
        assert "career_goal" in result
        assert "career_readiness" in result
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "roadmap" in result
        assert "recommended_projects" in result
        assert "estimated_weeks" in result

    def test_analyze_readiness_partial(self, orchestrator):
        assessment, _ = orchestrator.analyze(
            user_skills=["Linux"],
            career_goal="SOC Analyst",
        )
        assert 0 < assessment.readiness_score < 100

    def test_analyze_all_skills(self, orchestrator):
        from knowledge.loader import knowledge_loader
        role = knowledge_loader.get_role("SOC Analyst")
        assert role is not None
        all_skills = role["required_skills"] + role.get("optional_skills", [])
        assessment, _ = orchestrator.analyze(
            user_skills=all_skills,
            career_goal="SOC Analyst",
        )
        assert assessment.readiness_score == 100
