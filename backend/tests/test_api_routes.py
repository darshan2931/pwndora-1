import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data


class TestCareersEndpoint:
    def test_get_careers(self, client):
        response = client.get("/api/v1/careers")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0

    def test_careers_have_required_fields(self, client):
        response = client.get("/api/v1/careers")
        data = response.json()
        for career in data["data"]:
            assert "id" in career
            assert "title" in career
            assert "description" in career


class TestSkillsEndpoint:
    def test_get_skills(self, client):
        response = client.get("/api/v1/knowledge/skills")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "categories" in data["data"]


class TestCareerAnalyzeEndpoint:
    def test_analyze_with_manual_skills(self, client):
        response = client.post(
            "/api/v1/career/analyze",
            data={
                "career_goal": "SOC Analyst",
                "study_hours": 10,
                "manual_skills": "Linux, Python, SIEM",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "career_readiness" in data["data"]
        assert "matched_skills" in data["data"]
        assert "missing_skills" in data["data"]
        assert "roadmap" in data["data"]

    def test_analyze_without_skills_or_resume(self, client):
        response = client.post(
            "/api/v1/career/analyze",
            data={"career_goal": "SOC Analyst", "study_hours": 10},
        )
        assert response.status_code == 400

    def test_analyze_returns_roadmap_steps(self, client):
        response = client.post(
            "/api/v1/career/analyze",
            data={
                "career_goal": "SOC Analyst",
                "study_hours": 10,
                "manual_skills": "Linux",
            },
        )
        data = response.json()
        roadmap = data["data"]["roadmap"]
        assert isinstance(roadmap, list)
        assert len(roadmap) > 0
        for step in roadmap:
            assert "step" in step
            assert "skill" in step
            assert "estimated_hours" in step


class TestProjectsEndpoint:
    def test_get_projects(self, client):
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0

    def test_get_projects_for_skill(self, client):
        response = client.get("/api/v1/projects/Python")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestCertificationsEndpoint:
    def test_get_certifications_for_role(self, client):
        response = client.get("/api/v1/certifications/SOC Analyst")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
