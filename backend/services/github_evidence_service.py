import logging
import os
from datetime import datetime, timezone
from typing import Optional, Dict, List

from services.github_url_parser import GitHubURLParser
from services.github_api_service import GitHubAPIService
from services.repo_selector import RepoSelector
from services.tech_evidence_extractor import TechEvidenceExtractor
from schemas.github_evidence import (
    GitHubUserProfile,
    RepositoryMetadata,
    ReadmeData,
    TechEvidenceItem,
    RepositoryEvidence,
    RepoAIAnalysis,
    GitHubAnalysisResult,
)

logger = logging.getLogger(__name__)


class GitHubEvidenceService:

    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.api = GitHubAPIService()
        self.cache_minutes = int(os.getenv("GITHUB_CACHE_MINUTES", "60"))
        self.max_repos = int(os.getenv("GITHUB_MAX_REPOSITORIES", "10"))

    async def analyze(
        self,
        github_url: str,
        resume_profile_id: str = None,
        user_id: str = None,
        force_refresh: bool = False,
    ) -> GitHubAnalysisResult:
        parsed = GitHubURLParser.parse(github_url)
        if not parsed:
            return GitHubAnalysisResult(
                status="invalid_url",
                message="Could not extract a valid GitHub username from the provided URL.",
            )

        username = parsed["username"]

        if not force_refresh and user_id:
            cached = self._check_cache(username, user_id)
            if cached:
                return cached

        user_data = self.api.get_user(username)
        if not user_data:
            return GitHubAnalysisResult(
                status="user_not_found",
                message=f"GitHub user '{username}' was not found or the API is unavailable.",
            )

        github_profile = GitHubUserProfile(
            username=username,
            profile_url=f"https://github.com/{username}",
            avatar_url=user_data.get("avatar_url"),
            public_repositories=user_data.get("public_repos", 0),
            followers=user_data.get("followers", 0),
            following=user_data.get("following", 0),
            account_created_at=user_data.get("created_at"),
        )

        raw_repos = self.api.get_repositories(username)
        if not raw_repos:
            return GitHubAnalysisResult(
                status="completed",
                github_profile=github_profile,
                repositories_analyzed=0,
                repositories=[],
                all_technologies=[],
            )

        selector = RepoSelector(max_repos=self.max_repos)
        selected = selector.select(raw_repos)

        repo_evidences = []
        all_tech_evidence = []

        for repo_meta in selected:
            full_name = repo_meta["full_name"]

            languages = self.api.get_languages(full_name)
            repo_meta["languages"] = languages

            topics = self.api.get_topics(full_name)
            repo_meta["topics"] = topics

            readme_data = self.api.get_readme(full_name)
            repo_meta["has_readme"] = readme_data.get("readme_available", False)

            dep_files = self._fetch_dependency_files(full_name, languages)

            tech_evidence = TechEvidenceExtractor.extract_all(
                languages=languages,
                topics=topics,
                repo_name=repo_meta["name"],
                readme_text=readme_data.get("readme_text"),
                dependency_files=dep_files,
            )

            ai_analysis = await self._analyze_repo_with_ai(
                repo_meta=repo_meta,
                readme_text=readme_data.get("readme_text"),
                dep_files=dep_files,
            )

            repo_evidence = RepositoryEvidence(
                repository=RepositoryMetadata(**repo_meta),
                readme=ReadmeData(
                    readme_available=readme_data.get("readme_available", False),
                    readme_text=readme_data.get("readme_text", "")[:5000] if readme_data.get("readme_text") else None,
                    readme_character_count=readme_data.get("readme_character_count", 0),
                ),
                tech_evidence=tech_evidence,
                ai_analysis=ai_analysis,
            )
            repo_evidences.append(repo_evidence)
            all_tech_evidence.extend(tech_evidence)

        return GitHubAnalysisResult(
            status="completed",
            github_profile=github_profile,
            repositories_analyzed=len(repo_evidences),
            repositories=repo_evidences,
            all_technologies=all_tech_evidence,
        )

    def _fetch_dependency_files(self, full_name: str, languages: Dict[str, int]) -> Dict[str, str]:
        files = {}
        candidates = []
        lang_keys = {k.lower() for k in languages.keys()} if languages else set()

        if any(k in lang_keys for k in ("python",)):
            candidates.extend(["requirements.txt", "pyproject.toml", "Pipfile"])
        if any(k in lang_keys for k in ("javascript", "typescript")):
            candidates.append("package.json")
        if any(k in lang_keys for k in ("java",)):
            candidates.extend(["pom.xml", "build.gradle"])
        if any(k in lang_keys for k in ("go",)):
            candidates.append("go.mod")
        if any(k in lang_keys for k in ("rust",)):
            candidates.append("Cargo.toml")

        if not candidates:
            candidates = ["requirements.txt", "package.json", "pom.xml", "go.mod"]

        for filename in candidates:
            content = self.api.get_file_content(full_name, filename)
            if content:
                files[filename] = content

        return files

    async def _analyze_repo_with_ai(
        self,
        repo_meta: Dict,
        readme_text: Optional[str],
        dep_files: Optional[Dict[str, str]],
    ) -> Optional[RepoAIAnalysis]:
        if not self.ai_service:
            return None

        try:
            ai_input = {
                "repository_name": repo_meta.get("name", ""),
                "full_name": repo_meta.get("full_name", ""),
                "description": repo_meta.get("description", ""),
                "topics": repo_meta.get("topics", []),
                "languages": repo_meta.get("languages", {}),
                "dependencies": list(dep_files.keys()) if dep_files else [],
                "readme": (readme_text or "")[:4000],
            }

            task_prompt = f"Analyze this GitHub repository:\n\n{_format_ai_input(ai_input)}"

            raw_json = await self.ai_service.orchestrator.execute_task(
                task_prompt=task_prompt,
                template_name="repo_analysis",
                json_mode=True,
            )

            if raw_json is None:
                return None

            return _validate_analysis(raw_json)

        except Exception as e:
            logger.warning("AI analysis failed for repo %s: %s", repo_meta.get("name"), e)
            return None

    def _check_cache(self, username: str, user_id: str) -> Optional[GitHubAnalysisResult]:
        try:
            from repositories.repositories import GitHubProfileRepository, GitHubRepositoryEvidenceRepository
            profile_repo = GitHubProfileRepository()
            evidence_repo = GitHubRepositoryEvidenceRepository()

            gh_profile = profile_repo.get_latest_by_user_id(user_id)
            if not gh_profile:
                return None
            if gh_profile.username != username:
                return None
            if gh_profile.processing_status != "completed":
                return None
            if gh_profile.fetched_at:
                try:
                    fetched = gh_profile.fetched_at
                    now = datetime.now(timezone.utc)
                    if fetched.tzinfo is None:
                        from datetime import timezone as tz
                        fetched = fetched.replace(tzinfo=tz.utc)
                    diff = (now - fetched).total_seconds() / 60
                    if diff < self.cache_minutes:
                        return self._build_result_from_db(gh_profile, evidence_repo.get_by_profile_id(str(gh_profile.id)))
                except Exception:
                    pass
            return None
        except Exception as e:
            logger.debug("Cache check failed: %s", e)
            return None

    def _build_result_from_db(self, gh_profile, repo_evidences) -> GitHubAnalysisResult:
        github_user = GitHubUserProfile(
            username=gh_profile.username,
            profile_url=gh_profile.profile_url,
            avatar_url=gh_profile.avatar_url,
            public_repositories=gh_profile.public_repositories,
            followers=gh_profile.followers,
            following=gh_profile.following,
            account_created_at=gh_profile.account_created_at,
        )
        repos = []
        all_tech = []
        for re_ in (repo_evidences or []):
            tech_items = re_.tech_evidence or []
            all_tech.extend([TechEvidenceItem(**t) if isinstance(t, dict) else t for t in tech_items])
            repos.append(RepositoryEvidence(
                repository=RepositoryMetadata(
                    name=re_.repository_name,
                    full_name=re_.full_name,
                    description=re_.description,
                    html_url=re_.repository_url,
                    stars=re_.stars,
                    forks=re_.forks,
                    is_fork=bool(re_.is_fork),
                    is_archived=bool(re_.is_archived),
                    topics=re_.topics or [],
                    languages=re_.languages or {},
                    has_readme=bool(re_.readme_available),
                    selection_reasons=re_.selection_reasons or [],
                ),
                readme=ReadmeData(
                    readme_available=bool(re_.readme_available),
                    readme_text=re_.readme_text[:5000] if re_.readme_text else None,
                    readme_character_count=len(re_.readme_text) if re_.readme_text else 0,
                ),
                tech_evidence=[TechEvidenceItem(**t) if isinstance(t, dict) else t for t in tech_items],
                ai_analysis=RepoAIAnalysis(**re_.ai_analysis) if re_.ai_analysis else None,
            ))
        return GitHubAnalysisResult(
            status="completed",
            github_profile=github_user,
            repositories_analyzed=len(repos),
            repositories=repos,
            all_technologies=all_tech,
        )


def _format_ai_input(data: Dict) -> str:
    lines = []
    lines.append(f"Repository: {data.get('full_name', '')}")
    lines.append(f"Description: {data.get('description', '') or 'None'}")
    lines.append(f"Topics: {', '.join(data.get('topics', [])) or 'None'}")
    lines.append(f"Languages: {data.get('languages', {})}")
    if data.get("dependencies"):
        lines.append(f"Dependency files found: {', '.join(data['dependencies'])}")
    if data.get("readme"):
        lines.append(f"\nREADME excerpt:\n{data['readme'][:3000]}")
    return "\n".join(lines)


def _validate_analysis(raw: dict) -> Optional[RepoAIAnalysis]:
    try:
        data = raw if isinstance(raw, dict) else {}
        cybersecurity = data.get("cybersecurity_relevance", {})
        if not isinstance(cybersecurity, dict):
            cybersecurity = {}
        demonstrated = data.get("demonstrated_technologies", [])
        clean_demos = []
        for d in (demonstrated if isinstance(demonstrated, list) else []):
            if isinstance(d, dict) and d.get("name"):
                clean_demos.append({"name": str(d["name"]), "evidence": str(d.get("evidence", ""))})
        return RepoAIAnalysis(
            project_purpose=str(data.get("project_purpose")) if data.get("project_purpose") else None,
            technical_domains=[str(x) for x in (data.get("technical_domains") or []) if isinstance(x, str)],
            demonstrated_technologies=clean_demos,
            cybersecurity_relevance={
                "is_relevant": bool(cybersecurity.get("is_relevant", False)),
                "areas": [str(x) for x in (cybersecurity.get("areas") or []) if isinstance(x, str)],
                "evidence": str(cybersecurity.get("evidence")) if cybersecurity.get("evidence") else None,
            },
            complexity=str(data.get("complexity")) if data.get("complexity") else None,
            observable_evidence=[str(x) for x in (data.get("observable_evidence") or []) if isinstance(x, str)],
        )
    except Exception as e:
        logger.warning("Failed to validate AI analysis: %s", e)
        return None
