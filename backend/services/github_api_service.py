import os
import logging
import base64
import time
from typing import Optional, Dict, List

import httpx

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 15.0
DEPENDENCY_FILES = {
    "requirements.txt": "python",
    "pyproject.toml": "python",
    "Pipfile": "python",
    "package.json": "javascript",
    "package-lock.json": "javascript",
    "yarn.lock": "javascript",
    "pom.xml": "java",
    "build.gradle": "java",
    "go.mod": "go",
    "go.sum": "go",
    "*.csproj": "csharp",
    "Cargo.toml": "rust",
    "Gemfile": "ruby",
    "composer.json": "php",
}


class GitHubAPIService:
    """Public GitHub REST API client with optional token auth."""

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "").strip() or None
        self.timeout = float(os.getenv("GITHUB_API_TIMEOUT", str(DEFAULT_TIMEOUT)))
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _client(self) -> httpx.Client:
        return httpx.Client(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True,
        )

    def get_user(self, username: str) -> Optional[Dict]:
        try:
            with self._client() as client:
                r = client.get(f"{GITHUB_API_BASE}/users/{username}")
                if r.status_code == 200:
                    return r.json()
                if r.status_code == 404:
                    logger.warning("GitHub user not found: %s", username)
                    return None
                if r.status_code == 403:
                    logger.warning("GitHub rate limit hit for user %s", username)
                    return None
                logger.warning("GitHub API error %s for user %s", r.status_code, username)
                return None
        except httpx.TimeoutException:
            logger.warning("GitHub API timeout fetching user %s", username)
            return None
        except Exception as e:
            logger.error("GitHub API error fetching user %s: %s", username, e)
            return None

    def get_repositories(self, username: str, per_page: int = 100) -> List[Dict]:
        repos = []
        try:
            with self._client() as client:
                page = 1
                while page <= 3:
                    r = client.get(
                        f"{GITHUB_API_BASE}/users/{username}/repos",
                        params={"per_page": min(per_page, 100), "page": page, "sort": "updated"},
                    )
                    if r.status_code == 200:
                        batch = r.json()
                        if not batch:
                            break
                        repos.extend(batch)
                        if len(batch) < 100:
                            break
                        page += 1
                    else:
                        break
        except (httpx.TimeoutException, Exception) as e:
            logger.warning("Error fetching repos for %s: %s", username, e)
        return repos

    def get_languages(self, full_name: str) -> Dict[str, int]:
        try:
            with self._client() as client:
                r = client.get(f"{GITHUB_API_BASE}/repos/{full_name}/languages")
                if r.status_code == 200:
                    return r.json()
        except (httpx.TimeoutException, Exception):
            pass
        return {}

    def get_topics(self, full_name: str) -> List[str]:
        try:
            with self._client() as client:
                r = client.get(
                    f"{GITHUB_API_BASE}/repos/{full_name}/topics",
                    headers={**self.headers, "Accept": "application/vnd.github.mercy-preview+json"},
                )
                if r.status_code == 200:
                    return r.json().get("names", [])
        except (httpx.TimeoutException, Exception):
            pass
        return []

    def get_readme(self, full_name: str) -> Optional[Dict]:
        try:
            with self._client() as client:
                r = client.get(f"{GITHUB_API_BASE}/repos/{full_name}/readme")
                if r.status_code == 200:
                    data = r.json()
                    content = data.get("content", "")
                    encoding = data.get("encoding", "")
                    if encoding == "base64" and content:
                        try:
                            decoded = base64.b64decode(content).decode("utf-8", errors="replace")
                            return {
                                "readme_available": True,
                                "readme_text": decoded,
                                "readme_character_count": len(decoded),
                            }
                        except Exception:
                            pass
                    return {"readme_available": False, "readme_text": None, "readme_character_count": 0}
                if r.status_code == 404:
                    return {"readme_available": False, "readme_text": None, "readme_character_count": 0}
        except (httpx.TimeoutException, Exception):
            pass
        return {"readme_available": False, "readme_text": None, "readme_character_count": 0}

    def get_file_content(self, full_name: str, file_path: str) -> Optional[str]:
        try:
            with self._client() as client:
                r = client.get(f"{GITHUB_API_BASE}/repos/{full_name}/contents/{file_path}")
                if r.status_code == 200:
                    data = r.json()
                    content = data.get("content", "")
                    encoding = data.get("encoding", "")
                    if encoding == "base64" and content:
                        return base64.b64decode(content).decode("utf-8", errors="replace")
        except (httpx.TimeoutException, Exception):
            pass
        return None

    def get_rate_limit(self) -> Dict:
        try:
            with self._client() as client:
                r = client.get(f"{GITHUB_API_BASE}/rate_limit")
                if r.status_code == 200:
                    return r.json().get("resources", {}).get("core", {})
        except Exception:
            pass
        return {"remaining": 0, "limit": 60, "reset": 0}
