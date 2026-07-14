import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge.loader import KnowledgeLoader, knowledge_loader


class TestKnowledgeLoader:
    def test_get_roles_returns_list(self):
        roles = knowledge_loader.get_roles()
        assert isinstance(roles, list)
        assert len(roles) > 0

    def test_get_skills_returns_list(self):
        skills = knowledge_loader.get_skills()
        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_get_projects_returns_list(self):
        projects = knowledge_loader.get_projects()
        assert isinstance(projects, list)
        assert len(projects) > 0

    def test_get_certifications_returns_list(self):
        certs = knowledge_loader.get_certifications()
        assert isinstance(certs, list)
        assert len(certs) > 0

    def test_get_learning_paths_returns_list(self):
        paths = knowledge_loader.get_learning_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0

    def test_get_role_found(self):
        role = knowledge_loader.get_role("SOC Analyst")
        assert role is not None
        assert role["role"] == "SOC Analyst"
        assert "required_skills" in role

    def test_get_role_case_insensitive(self):
        role = knowledge_loader.get_role("soc analyst")
        assert role is not None

    def test_get_role_not_found(self):
        role = knowledge_loader.get_role("Nonexistent Role")
        assert role is None

    def test_get_skill_found(self):
        skill = knowledge_loader.get_skill("Linux")
        assert skill is not None
        assert skill["name"] == "Linux"
        assert "category" in skill

    def test_get_skill_case_insensitive(self):
        skill = knowledge_loader.get_skill("linux")
        assert skill is not None

    def test_get_skill_not_found(self):
        skill = knowledge_loader.get_skill("Nonexistent Skill")
        assert skill is None

    def test_get_projects_for_skill(self):
        projects = knowledge_loader.get_projects_for_skill("Python")
        assert isinstance(projects, list)
        for p in projects:
            assert "Python" in p["skills"]

    def test_get_projects_for_unknown_skill(self):
        projects = knowledge_loader.get_projects_for_skill("NonexistentSkill")
        assert projects == []

    def test_get_certifications_for_role(self):
        certs = knowledge_loader.get_certifications_for_role("SOC Analyst")
        assert isinstance(certs, list)
        for c in certs:
            assert "SOC Analyst" in c["recommended_for"]

    def test_get_certifications_for_unknown_role(self):
        certs = knowledge_loader.get_certifications_for_role("NonexistentRole")
        assert certs == []

    def test_get_learning_path_found(self):
        path = knowledge_loader.get_learning_path("SOC Analyst")
        assert path is not None
        assert path["career"] == "SOC Analyst"
        assert "sequence" in path

    def test_get_learning_path_not_found(self):
        path = knowledge_loader.get_learning_path("NonexistentRole")
        assert path is None

    def test_get_skill_prerequisites(self):
        prereqs = knowledge_loader.get_skill_prerequisites("SIEM")
        assert isinstance(prereqs, list)

    def test_get_skill_prerequisites_unknown(self):
        prereqs = knowledge_loader.get_skill_prerequisites("NonexistentSkill")
        assert prereqs == []

    def test_search_skills(self):
        results = knowledge_loader.search_skills("linux")
        assert len(results) > 0

    def test_search_skills_by_category(self):
        results = knowledge_loader.search_skills("networking")
        assert len(results) > 0

    def test_validate_all_no_errors(self):
        errors = knowledge_loader.validate_all()
        assert errors == []

    def test_cache_invalidation(self):
        knowledge_loader.get_skills()
        knowledge_loader.invalidate_cache("skills.json")
        assert "skills.json" not in knowledge_loader._cache

    def test_full_cache_invalidation(self):
        knowledge_loader.get_skills()
        knowledge_loader.get_roles()
        knowledge_loader.invalidate_cache()
        assert len(knowledge_loader._cache) == 0

    def test_cache_ttl_expiry(self):
        knowledge_loader.invalidate_cache()
        knowledge_loader.get_skills()
        assert "skills.json" in knowledge_loader._cache
        data, ts = knowledge_loader._cache["skills.json"]
        knowledge_loader._cache["skills.json"] = (data, time.time() - 400)
        knowledge_loader.invalidate_cache()
        knowledge_loader.get_skills()
        assert "skills.json" in knowledge_loader._cache
