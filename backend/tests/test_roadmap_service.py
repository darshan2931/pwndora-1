import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.models import Roadmap, Skill
from services.career_service import CareerService
from services.roadmap_service import RoadmapService


@pytest.fixture
def roadmap_service():
    return RoadmapService()


@pytest.fixture
def career_service():
    return CareerService()


@pytest.fixture
def sample_assessment(career_service):
    return career_service.analyze(
        user_skills=["Linux"],
        career_goal="SOC Analyst",
    )


class TestRoadmapService:
    def test_generate_returns_roadmap(self, roadmap_service, sample_assessment):
        roadmap = roadmap_service.generate(sample_assessment, study_hours=10)
        assert isinstance(roadmap, Roadmap)
        assert len(roadmap.steps) > 0
        assert roadmap.total_hours > 0
        assert roadmap.estimated_weeks > 0

    def test_generate_weekly_hours(self, roadmap_service, sample_assessment):
        roadmap = roadmap_service.generate(sample_assessment, study_hours=20)
        assert roadmap.estimated_weeks >= 1

    def test_order_by_prerequisites_basic(self, roadmap_service):
        skills = [
            Skill(name="SIEM", category="Defensive Security", difficulty="intermediate"),
            Skill(name="Log Analysis", category="Defensive Security", difficulty="beginner"),
        ]
        ordered = roadmap_service.order_by_prerequisites(skills)
        names = [s.name for s in ordered]
        assert names.index("Log Analysis") < names.index("SIEM")

    def test_order_by_prerequisites_no_deps(self, roadmap_service):
        skills = [
            Skill(name="Python", category="Programming", difficulty="beginner"),
            Skill(name="Linux", category="Operating Systems", difficulty="beginner"),
        ]
        ordered = roadmap_service.order_by_prerequisites(skills)
        assert len(ordered) == 2

    def test_order_by_prerequisites_empty(self, roadmap_service):
        ordered = roadmap_service.order_by_prerequisites([])
        assert ordered == []

    def test_estimate_weeks(self, roadmap_service):
        assert roadmap_service._estimate_weeks(40, 10) == 4
        assert roadmap_service._estimate_weeks(40, 20) == 2
        assert roadmap_service._estimate_weeks(5, 10) == 1
        assert roadmap_service._estimate_weeks(0, 10) == 1
        assert roadmap_service._estimate_weeks(40, 0) == 4

    def test_roadmap_summary(self, roadmap_service, sample_assessment):
        roadmap = roadmap_service.generate(sample_assessment)
        summary = roadmap_service.get_roadmap_summary(roadmap)
        assert "total_steps" in summary
        assert "total_hours" in summary
        assert "estimated_weeks" in summary
        assert "skills" in summary
        assert len(summary["skills"]) == summary["total_steps"]

    def test_steps_have_prerequisites(self, roadmap_service, sample_assessment):
        roadmap = roadmap_service.generate(sample_assessment)
        for step in roadmap.steps:
            assert isinstance(step.prerequisites, list)

    def test_steps_have_resources(self, roadmap_service, sample_assessment):
        roadmap = roadmap_service.generate(sample_assessment)
        for step in roadmap.steps:
            assert isinstance(step.resources, list)
