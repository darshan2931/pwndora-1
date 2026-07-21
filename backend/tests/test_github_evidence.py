import os
import json
import pytest
from unittest.mock import patch, MagicMock


# ─── GitHub URL Parser Tests ──────────────────────────────────────────────────

class TestGitHubURLParser:

    def setup_method(self):
        from services.github_url_parser import GitHubURLParser
        self.parser = GitHubURLParser

    def test_parse_standard_url(self):
        result = self.parser.parse("https://github.com/octocat")
        assert result is not None
        assert result["username"] == "octocat"
        assert result["profile_url"] == "https://github.com/octocat"

    def test_parse_www_url(self):
        result = self.parser.parse("https://www.github.com/octocat")
        assert result is not None
        assert result["username"] == "octocat"

    def test_parse_trailing_slash(self):
        result = self.parser.parse("https://github.com/octocat/")
        assert result is not None
        assert result["username"] == "octocat"

    def test_parse_url_with_hyphen(self):
        result = self.parser.parse("https://github.com/my-user")
        assert result is not None
        assert result["username"] == "my-user"

    def test_parse_url_with_underscore(self):
        result = self.parser.parse("https://github.com/my_user")
        assert result is not None
        assert result["username"] == "my_user"

    def test_parse_repo_url_returns_none(self):
        result = self.parser.parse("https://github.com/octocat/Hello-World")
        assert result is None

    def test_parse_invalid_domain(self):
        result = self.parser.parse("https://gitlab.com/octocat")
        assert result is None

    def test_parse_empty_string(self):
        assert self.parser.parse("") is None

    def test_parse_none(self):
        assert self.parser.parse(None) is None

    def test_parse_no_path(self):
        assert self.parser.parse("https://github.com") is None

    def test_parse_long_username(self):
        long_name = "a" * 40
        assert self.parser.parse(f"https://github.com/{long_name}") is None

    def test_parse_special_chars_rejected(self):
        assert self.parser.parse("https://github.com/user name") is None
        assert self.parser.parse("https://github.com/user@name") is None

    def test_extract_from_text(self):
        text = "Check https://github.com/alice and https://github.com/bob"
        usernames = self.parser.extract_from_text(text)
        assert "alice" in usernames
        assert "bob" in usernames

    def test_extract_from_text_no_duplicates(self):
        text = "https://github.com/alice and again https://github.com/alice"
        usernames = self.parser.extract_from_text(text)
        assert usernames.count("alice") == 1

    def test_extract_from_text_empty(self):
        assert self.parser.extract_from_text("") == []
        assert self.parser.extract_from_text(None) == []

    def test_is_profile_url(self):
        assert self.parser.is_profile_url("https://github.com/octocat") is True
        assert self.parser.is_profile_url("https://github.com/octocat/repo") is False
        assert self.parser.is_profile_url("https://gitlab.com/octocat") is False

    def test_is_repo_url(self):
        assert self.parser.is_repo_url("https://github.com/octocat/Hello-World") is True
        assert self.parser.is_repo_url("https://github.com/octocat") is False


# ─── Repository Selector Tests ────────────────────────────────────────────────

class TestRepoSelector:

    def setup_method(self):
        from services.repo_selector import RepoSelector
        self.selector = RepoSelector(max_repos=3)

    def _make_repo(self, name, **kwargs):
        defaults = {
            "name": name,
            "full_name": f"user/{name}",
            "description": f"Project {name}",
            "html_url": f"https://github.com/user/{name}",
            "fork": False,
            "archived": False,
            "stargazers_count": 0,
            "forks_count": 0,
            "pushed_at": "2026-07-01T00:00:00Z",
            "topics": [],
            "size": 500,
            "default_branch": "main",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2026-07-01T00:00:00Z",
        }
        defaults.update(kwargs)
        return defaults

    def test_fork_excluded(self):
        repos = [self._make_repo("forked", fork=True)]
        result = self.selector.select(repos)
        assert len(result) == 0

    def test_archived_excluded(self):
        repos = [self._make_repo("old", archived=True)]
        result = self.selector.select(repos)
        assert len(result) == 0

    def test_limit_repos(self):
        repos = [self._make_repo(f"repo{i}") for i in range(10)]
        result = self.selector.select(repos)
        assert len(result) <= 3

    def test_recently_updated_highest_score(self):
        repos = [
            self._make_repo("old", pushed_at="2024-01-01T00:00:00Z"),
            self._make_repo("new", pushed_at="2026-07-20T00:00:00Z"),
        ]
        result = self.selector.select(repos)
        assert result[0]["name"] == "new"

    def test_stars_boost_score(self):
        repos = [
            self._make_repo("no-stars", stargazers_count=0),
            self._make_repo("many-stars", stargazers_count=50),
        ]
        result = self.selector.select(repos)
        assert result[0]["name"] == "many-stars"

    def test_selection_reasons_present(self):
        repos = [self._make_repo("test")]
        result = self.selector.select(repos)
        assert "non-fork" in result[0]["selection_reasons"]

    def test_empty_repos(self):
        result = self.selector.select([])
        assert result == []


# ─── Tech Evidence Extractor Tests ────────────────────────────────────────────

class TestTechEvidenceExtractor:

    def setup_method(self):
        from services.tech_evidence_extractor import TechEvidenceExtractor
        self.extractor = TechEvidenceExtractor

    def test_extract_from_languages(self):
        evidence = self.extractor.extract_from_languages(
            {"Python": 5000, "JavaScript": 3000}, "test-repo"
        )
        assert len(evidence) == 2
        assert evidence[0]["technology"] == "Python"
        assert evidence[0]["evidence_type"] == "repository_language"
        assert evidence[0]["details"]["percentage"] > 0

    def test_extract_from_languages_empty(self):
        evidence = self.extractor.extract_from_languages({}, "test-repo")
        assert len(evidence) == 0

    def test_extract_from_topics(self):
        evidence = self.extractor.extract_from_topics(
            ["cybersecurity", "python", "api"], "test-repo"
        )
        assert len(evidence) == 3
        assert evidence[0]["evidence_type"] == "repository_topic"

    def test_parse_requirements_txt(self):
        content = "flask>=2.0\nrequests\n# comment\npytest>=7.0"
        deps = self.extractor._parse_requirements_txt(content)
        assert "flask" in deps
        assert "requests" in deps
        assert "pytest" in deps
        assert "# comment" not in deps

    def test_parse_package_json(self):
        content = json.dumps({
            "dependencies": {"react": "^18.0.0", "next": "14.0.0"},
            "devDependencies": {"typescript": "^5.0.0"}
        })
        deps = self.extractor._parse_package_json(content)
        assert "react" in deps
        assert "next" in deps
        assert "typescript" in deps

    def test_parse_package_json_invalid(self):
        deps = self.extractor._parse_package_json("not json")
        assert deps == []

    def test_extract_from_dependency_file(self):
        content = "flask>=2.0\nrequests"
        evidence = self.extractor.extract_from_dependency_file(
            content, "requirements.txt", "test-repo"
        )
        assert len(evidence) == 2
        assert evidence[0]["evidence_type"] == "dependency"
        assert evidence[0]["details"]["source_file"] == "requirements.txt"

    def test_extract_from_readme(self):
        readme = "This project uses Python and Docker for deployment with PostgreSQL database."
        evidence = self.extractor.extract_from_readme(readme, "test-repo")
        techs = [e["technology"].lower() for e in evidence]
        assert "python" in techs
        assert "docker" in techs

    def test_extract_from_readme_empty(self):
        assert self.extractor.extract_from_readme("", "test") == []
        assert self.extractor.extract_from_readme(None, "test") == []

    def test_extract_all(self):
        evidence = self.extractor.extract_all(
            languages={"Python": 1000},
            topics=["security"],
            repo_name="test-repo",
            readme_text="Uses Python for testing",
        )
        assert len(evidence) > 0

    def test_parse_pom_xml(self):
        content = "<artifactId>junit</artifactId><artifactId>spring-boot</artifactId>"
        deps = self.extractor._parse_pom_xml(content)
        assert "junit" in deps
        assert "spring-boot" in deps

    def test_parse_go_mod(self):
        content = "require (\n\tgithub.com/gin-gonic/gin v1.9.0\n\tgithub.com/stretchr/testify v1.8.0\n)"
        deps = self.extractor._parse_go_mod(content)
        assert "gin" in deps
        assert "testify" in deps


# ─── Pydantic Schema Tests ────────────────────────────────────────────────────

class TestGitHubSchemas:

    def setup_method(self):
        from schemas.github_evidence import (
            GitHubUserProfile, RepositoryMetadata, ReadmeData,
            TechEvidenceItem, RepoAIAnalysis, GitHubAnalysisResult,
            GitHubProfileResponse, GitHubEvidenceResponse,
        )
        self.schemas = {
            "GitHubUserProfile": GitHubUserProfile,
            "RepositoryMetadata": RepositoryMetadata,
            "ReadmeData": ReadmeData,
            "TechEvidenceItem": TechEvidenceItem,
            "RepoAIAnalysis": RepoAIAnalysis,
            "GitHubAnalysisResult": GitHubAnalysisResult,
            "GitHubProfileResponse": GitHubProfileResponse,
            "GitHubEvidenceResponse": GitHubEvidenceResponse,
        }

    def test_github_user_profile(self):
        from schemas.github_evidence import GitHubUserProfile
        p = GitHubUserProfile(username="octocat", profile_url="https://github.com/octocat")
        assert p.username == "octocat"
        assert p.followers == 0

    def test_tech_evidence_item(self):
        from schemas.github_evidence import TechEvidenceItem
        t = TechEvidenceItem(technology="Python", evidence_type="repository_language", repository="test")
        assert t.source == "github"

    def test_repo_ai_analysis_defaults(self):
        from schemas.github_evidence import RepoAIAnalysis
        a = RepoAIAnalysis()
        assert a.technical_domains == []
        assert a.cybersecurity_relevance.is_relevant is False

    def test_github_analysis_result_defaults(self):
        from schemas.github_evidence import GitHubAnalysisResult
        r = GitHubAnalysisResult(status="completed")
        assert r.repositories == []
        assert r.all_technologies == []


# ─── AI Prompt Tests ──────────────────────────────────────────────────────────

class TestAIPrompt:

    def test_repo_analysis_prompt_exists(self):
        path = os.path.join(
            os.path.dirname(__file__), "..", "app", "ai", "prompts", "repo_analysis.md"
        )
        assert os.path.exists(path), "repo_analysis.md prompt template missing"

    def test_repo_analysis_prompt_has_schema(self):
        path = os.path.join(
            os.path.dirname(__file__), "..", "app", "ai", "prompts", "repo_analysis.md"
        )
        content = open(path).read()
        assert "project_purpose" in content
        assert "technical_domains" in content
        assert "demonstrated_technologies" in content
        assert "cybersecurity_relevance" in content
        assert "complexity" in content


# ─── Database Model Tests ─────────────────────────────────────────────────────

class TestGitHubModels:

    def test_github_profile_model_fields(self):
        from models.sqlalchemy_models import GitHubProfile
        columns = {c.name for c in GitHubProfile.__table__.columns}
        expected = {
            "id", "user_id", "resume_profile_id", "username", "profile_url",
            "avatar_url", "public_repositories", "followers", "following",
            "account_created_at", "fetched_at", "processing_status",
            "processing_error", "created_at", "updated_at",
        }
        assert expected.issubset(columns)

    def test_github_repo_evidence_model_fields(self):
        from models.sqlalchemy_models import GitHubRepositoryEvidence
        columns = {c.name for c in GitHubRepositoryEvidence.__table__.columns}
        expected = {
            "id", "github_profile_id", "repository_name", "full_name",
            "description", "repository_url", "languages", "topics",
            "dependencies", "readme_text", "readme_available", "stars",
            "forks", "is_fork", "is_archived", "created_at_github",
            "updated_at_github", "pushed_at_github", "selection_reasons",
            "ai_analysis", "tech_evidence", "created_at", "updated_at",
        }
        assert expected.issubset(columns)


# ─── Repository Class Tests ───────────────────────────────────────────────────

class TestGitHubRepositories:

    def test_github_profile_repo_has_methods(self):
        from repositories.repositories import GitHubProfileRepository
        repo = GitHubProfileRepository()
        assert hasattr(repo, "get_by_id")
        assert hasattr(repo, "get_latest_by_user_id")
        assert hasattr(repo, "create")
        assert hasattr(repo, "update_status")
        assert hasattr(repo, "update_result")
        assert hasattr(repo, "delete")

    def test_github_evidence_repo_has_methods(self):
        from repositories.repositories import GitHubRepositoryEvidenceRepository
        repo = GitHubRepositoryEvidenceRepository()
        assert hasattr(repo, "get_by_profile_id")
        assert hasattr(repo, "create")
        assert hasattr(repo, "create_many")
        assert hasattr(repo, "delete_by_profile_id")


# ─── GitHub API Service Tests ─────────────────────────────────────────────────

class TestGitHubAPIService:

    def setup_method(self):
        from services.github_api_service import GitHubAPIService
        self.service = GitHubAPIService()

    def test_has_expected_methods(self):
        assert hasattr(self.service, "get_user")
        assert hasattr(self.service, "get_repositories")
        assert hasattr(self.service, "get_languages")
        assert hasattr(self.service, "get_topics")
        assert hasattr(self.service, "get_readme")
        assert hasattr(self.service, "get_file_content")
        assert hasattr(self.service, "get_rate_limit")

    def test_token_loaded_from_env(self):
        token = os.getenv("GITHUB_TOKEN", "")
        if token:
            assert self.service.token == token
        else:
            assert self.service.token is None


# ─── GitHub Evidence Service Tests ────────────────────────────────────────────

class TestGitHubEvidenceService:

    def setup_method(self):
        from services.github_evidence_service import GitHubEvidenceService
        self.service = GitHubEvidenceService(ai_service=None)

    def test_has_expected_methods(self):
        assert hasattr(self.service, "analyze")

    def test_invalid_url_returns_error(self):
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            self.service.analyze("not-a-url")
        )
        assert result.status == "invalid_url"

    def test_empty_url_returns_error(self):
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            self.service.analyze("")
        )
        assert result.status == "invalid_url"


# ─── API Endpoint Protection Tests ────────────────────────────────────────────

class TestGitHubAPIProtection:

    def test_analyze_requires_auth(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        res = client.post("/api/v1/github/analyze")
        assert res.status_code in (401, 403)

    def test_profile_requires_auth(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        res = client.get("/api/v1/github/profile")
        assert res.status_code in (401, 403)

    def test_evidence_requires_auth(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        res = client.get("/api/v1/github/evidence")
        assert res.status_code in (401, 403)


# ─── Caching Tests ────────────────────────────────────────────────────────────

class TestGitHubCaching:

    def test_cache_minutes_configurable(self):
        from services.github_evidence_service import GitHubEvidenceService
        with patch.dict(os.environ, {"GITHUB_CACHE_MINUTES": "30"}):
            svc = GitHubEvidenceService()
            assert svc.cache_minutes == 30

    def test_max_repos_configurable(self):
        from services.github_evidence_service import GitHubEvidenceService
        with patch.dict(os.environ, {"GITHUB_MAX_REPOSITORIES": "5"}):
            svc = GitHubEvidenceService()
            assert svc.max_repos == 5

    def test_default_max_repos(self):
        from services.github_evidence_service import GitHubEvidenceService
        with patch.dict(os.environ, {}, clear=True):
            svc = GitHubEvidenceService()
            assert svc.max_repos == 10
