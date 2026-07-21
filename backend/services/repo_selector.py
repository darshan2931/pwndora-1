import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RepoSelector:
    """Deterministic repository selection with scoring and reasoning."""

    def __init__(self, max_repos: int = 10):
        self.max_repos = max_repos

    def select(self, repos: List[Dict]) -> List[Dict]:
        candidates = []
        for repo in repos:
            if repo.get("fork"):
                continue
            if repo.get("archived"):
                continue
            score, reasons = self._score_repo(repo)
            candidates.append({
                "repo": repo,
                "score": score,
                "reasons": reasons,
            })
        candidates.sort(key=lambda x: (-x["score"], x["repo"].get("pushed_at") or ""))
        selected = candidates[:self.max_repos]
        result = []
        for item in selected:
            repo = item["repo"]
            result.append({
                "name": repo.get("name", ""),
                "full_name": repo.get("full_name", ""),
                "description": repo.get("description") or "",
                "html_url": repo.get("html_url", ""),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "is_fork": repo.get("fork", False),
                "is_archived": repo.get("archived", False),
                "topics": repo.get("topics", []),
                "languages": {},
                "default_branch": repo.get("default_branch", "main"),
                "size": repo.get("size", 0),
                "has_readme": False,
                "selection_reasons": item["reasons"],
            })
        return result

    def _score_repo(self, repo: Dict) -> tuple:
        score = 0
        reasons = []

        if repo.get("pushed_at"):
            try:
                pushed = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                days = (now - pushed).days
                if days <= 30:
                    score += 30
                    reasons.append("recently updated")
                elif days <= 90:
                    score += 20
                    reasons.append("updated in last 3 months")
                elif days <= 365:
                    score += 10
                    reasons.append("updated in last year")
            except (ValueError, TypeError):
                pass

        stars = repo.get("stargazers_count", 0)
        if stars >= 100:
            score += 25
            reasons.append(f"{stars} stars")
        elif stars >= 10:
            score += 15
            reasons.append(f"{stars} stars")
        elif stars >= 1:
            score += 5
            reasons.append(f"{stars} stars")

        if not repo.get("fork"):
            score += 10
            reasons.append("non-fork")

        desc = (repo.get("description") or "").strip()
        if len(desc) > 20:
            score += 5
            reasons.append("has description")

        if repo.get("size", 0) > 100:
            score += 5
            reasons.append("contains code")
        else:
            reasons.append("appears empty or minimal")

        return score, reasons
