import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.models import UserProfile
from services.resume_service import ResumeService


@pytest.fixture
def resume_service():
    return ResumeService()


class TestResumeService:
    def test_extract_skills_from_text(self, resume_service):
        text = "I have experience with Linux, Python, and SIEM tools like Splunk."
        skills = resume_service.extract_skills(text)
        skill_names = [s.name for s in skills]
        assert "Linux" in skill_names
        assert "Python" in skill_names

    def test_extract_skills_empty_text(self, resume_service):
        skills = resume_service.extract_skills("")
        assert skills == []

    def test_extract_skills_none_text(self, resume_service):
        skills = resume_service.extract_skills(None)
        assert skills == []

    def test_extract_skills_no_matches(self, resume_service):
        text = "I like cooking and gardening."
        skills = resume_service.extract_skills(text)
        assert len(skills) == 0

    def test_extract_skills_multiple_categories(self, resume_service):
        text = "Skilled in Linux, Python, Burp Suite, AWS, and Docker."
        skills = resume_service.extract_skills(text)
        categories = {s.category for s in skills}
        assert len(categories) > 1

    def test_detect_certifications(self, resume_service):
        text = "I hold a CompTIA Security+ certification."
        certs = resume_service._detect_certifications(text)
        assert "CompTIA Security+" in certs

    def test_detect_certifications_none(self, resume_service):
        text = "I have no certifications."
        certs = resume_service._detect_certifications(text)
        assert certs == []

    def test_extract_text_txt_file(self, resume_service):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Linux Python SIEM")
            temp_path = f.name
        try:
            text = resume_service._extract_text(temp_path)
            assert "Linux" in text
        finally:
            os.unlink(temp_path)

    def test_extract_text_nonexistent_file(self, resume_service):
        text = resume_service._extract_text("/nonexistent/file.txt")
        assert text == ""

    def test_parse_returns_user_profile(self, resume_service):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Experience with Linux and Python.")
            temp_path = f.name
        try:
            profile = resume_service.parse(temp_path)
            assert isinstance(profile, UserProfile)
            assert len(profile.skills) > 0
        finally:
            os.unlink(temp_path)
