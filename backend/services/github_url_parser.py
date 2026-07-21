import re
import logging
from typing import Optional, Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

GITHUB_URL_PATTERN = re.compile(
    r'https?://(?:www\.)?github\.com/([A-Za-z0-9_-]+)(?:/[A-Za-z0-9_.-]+)?(?:/)?',
    re.IGNORECASE,
)


class GitHubURLParser:

    @staticmethod
    def parse_username(url: str) -> Optional[str]:
        if not url:
            return None
        url = url.strip().rstrip("/")
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        if host != "github.com":
            return None
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) != 1:
            return None
        username = parts[0]
        if not re.match(r'^[A-Za-z0-9_-]+$', username):
            return None
        if len(username) > 39:
            return None
        return username

    @staticmethod
    def extract_from_text(text: str) -> list:
        if not text:
            return []
        matches = GITHUB_URL_PATTERN.findall(text)
        seen = set()
        result = []
        for username in matches:
            username = username.strip().rstrip("/")
            if username not in seen and re.match(r'^[A-Za-z0-9_-]+$', username):
                seen.add(username)
                result.append(username)
        return result

    @staticmethod
    def parse(url: str) -> Optional[Dict]:
        username = GitHubURLParser.parse_username(url)
        if not username:
            return None
        return {
            "username": username,
            "profile_url": f"https://github.com/{username}",
        }

    @staticmethod
    def is_profile_url(url: str) -> bool:
        if not url:
            return False
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        if host != "github.com":
            return False
        parts = [p for p in parsed.path.split("/") if p]
        return len(parts) == 1

    @staticmethod
    def is_repo_url(url: str) -> bool:
        if not url:
            return False
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        if host != "github.com":
            return False
        parts = [p for p in parsed.path.split("/") if p]
        return len(parts) >= 2
