import re
import logging
from typing import List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(
    r'https?://[^\s<>"\')\]]+',
    re.IGNORECASE,
)


class ResumeURLExtractor:

    @staticmethod
    def extract(text: str) -> dict:
        if not text:
            return {"github": [], "linkedin": [], "portfolio": [], "personal_website": [], "other": []}

        raw_urls = URL_PATTERN.findall(text)
        cleaned = []
        for url in raw_urls:
            url = url.rstrip(".,;:!?)")
            if url.endswith(")"):
                url = url[:-1]
            cleaned.append(ResumeURLExtractor._normalize(url))

        seen = set()
        unique = []
        for u in cleaned:
            if u not in seen:
                seen.add(u)
                unique.append(u)

        result = {
            "github": [],
            "linkedin": [],
            "portfolio": [],
            "personal_website": [],
            "other": [],
        }

        for url in unique:
            domain = ResumeURLExtractor._get_domain(url)
            if not domain:
                continue

            if "github.com" in domain:
                result["github"].append(url)
            elif "linkedin.com" in domain:
                result["linkedin"].append(url)
            elif ResumeURLExtractor._is_portfolio_url(url, domain, text):
                result["portfolio"].append(url)
            elif ResumeURLExtractor._is_personal_website(url, domain):
                result["personal_website"].append(url)
            else:
                result["other"].append(url)

        return result

    @staticmethod
    def _normalize(url: str) -> str:
        url = url.rstrip("/")
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if host.startswith("www."):
            host = host[4:]
        path = parsed.path.rstrip("/")
        if parsed.port and parsed.port in (80, 443):
            port = ""
        else:
            port = f":{parsed.port}" if parsed.port else ""
        scheme = parsed.scheme or "https"
        normalized = f"{scheme}://{host}{port}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized

    @staticmethod
    def _get_domain(url: str) -> str:
        try:
            parsed = urlparse(url)
            return (parsed.hostname or "").lower()
        except Exception:
            return ""

    @staticmethod
    def _is_portfolio_url(url: str, domain: str, text: str) -> bool:
        portfolio_indicators = ["portfolio", "personal", "devfolio", "codepen", "vercel.app", "netlify.app"]
        for indicator in portfolio_indicators:
            if indicator in domain or indicator in url.lower():
                return True
        text_lower = text.lower()
        if "portfolio" in text_lower or "personal website" in text_lower:
            return True
        return False

    @staticmethod
    def _is_personal_website(url: str, domain: str) -> bool:
        personal_indicators = [".dev", ".io", ".me", ".tech", ".xyz", ".site", ".online"]
        for ext in personal_indicators:
            if domain.endswith(ext):
                return True
        if domain.count(".") == 1 and not domain.endswith((".com", ".org", ".net", ".edu", ".gov")):
            return True
        return False
