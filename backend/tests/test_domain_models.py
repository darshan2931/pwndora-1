import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.models import (
    Assessment,
    Career,
    Project,
    Roadmap,
    RoadmapStep,
    Skill,
    UserProfile,
)


class TestSkill:
    def test_create_skill(self):
        skill = Skill(name="Linux", category="Operating Systems", difficulty="beginner")
        assert skill.name == "Linux"
        assert skill.category == "Operating Systems"
        assert skill.difficulty == "beginner"

    def test_skill_defaults(self):
        skill = Skill(name="Python", category="Programming", difficulty="beginner")
        assert skill.prerequisites == []
        assert skill.estimated_hours == 10
        assert skill.related_tools == []
        assert skill.learning_resources == []


class TestCareer:
    def test_create_career(self):
        career = Career(
            id="soc-analyst",
            title="SOC Analyst",
            description="Monitors security alerts",
            required_skills=["Linux", "SIEM"],
        )
        assert career.title == "SOC Analyst"
        assert len(career.required_skills) == 2

    def test_career_defaults(self):
        career = Career(id="test", title="Test", description="", required_skills=[])
        assert career.optional_skills == []
        assert career.recommended_certifications == []
        assert career.suggested_projects == []


class TestUserProfile:
    def test_create_profile(self):
        profile = UserProfile(
            name="Test User",
            skills=[Skill(name="Linux", category="OS", difficulty="beginner")],
            certifications=["Security+"],
            experience_years=2,
        )
        assert profile.name == "Test User"
        assert len(profile.skills) == 1
        assert profile.experience_years == 2

    def test_profile_defaults(self):
        profile = UserProfile()
        assert profile.name is None
        assert profile.skills == []
        assert profile.certifications == []
        assert profile.experience_years == 0


class TestAssessment:
    def test_create_assessment(self):
        assessment = Assessment(
            user_profile=UserProfile(),
            target_career=Career(id="t", title="T", description="", required_skills=[]),
            matched_skills=[Skill(name="Linux", category="OS", difficulty="beginner")],
            missing_skills=[Skill(name="SIEM", category="Def", difficulty="intermediate")],
            readiness_score=50,
        )
        assert assessment.readiness_score == 50
        assert len(assessment.matched_skills) == 1
        assert len(assessment.missing_skills) == 1


class TestRoadmap:
    def test_create_roadmap(self):
        roadmap = Roadmap(
            steps=[
                RoadmapStep(
                    step=1,
                    skill=Skill(name="Linux", category="OS", difficulty="beginner"),
                    estimated_hours=20,
                )
            ],
            total_hours=20,
            estimated_weeks=2,
        )
        assert len(roadmap.steps) == 1
        assert roadmap.total_hours == 20
        assert roadmap.estimated_weeks == 2

    def test_roadmap_defaults(self):
        roadmap = Roadmap()
        assert roadmap.steps == []
        assert roadmap.total_hours == 0
        assert roadmap.estimated_weeks == 0


class TestProject:
    def test_create_project(self):
        project = Project(
            title="Port Scanner",
            difficulty="Easy",
            skills_demonstrated=["Python", "Networking"],
            estimated_time_hours=8,
        )
        assert project.title == "Port Scanner"
        assert project.difficulty == "Easy"

    def test_project_defaults(self):
        project = Project(
            title="Test", difficulty="Easy", skills_demonstrated=[], estimated_time_hours=5
        )
        assert project.description == ""
        assert project.github_deliverables == []
