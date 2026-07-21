import json
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DEPENDENCY_PARSERS = {
    "requirements.txt": "_parse_requirements_txt",
    "pyproject.toml": "_parse_pyproject_toml",
    "Pipfile": "_parse_pipfile",
    "package.json": "_parse_package_json",
    "pom.xml": "_parse_pom_xml",
    "build.gradle": "_parse_build_gradle",
    "go.mod": "_parse_go_mod",
}


class TechEvidenceExtractor:

    @staticmethod
    def extract_from_languages(languages: Dict[str, int], repo_name: str) -> List[Dict]:
        evidence = []
        total = sum(languages.values()) if languages else 0
        if total == 0:
            return evidence
        for lang, bytes_count in sorted(languages.items(), key=lambda x: -x[1]):
            pct = round((bytes_count / total) * 100, 1)
            evidence.append({
                "technology": lang,
                "source": "github",
                "evidence_type": "repository_language",
                "repository": repo_name,
                "details": {"percentage": pct},
            })
        return evidence

    @staticmethod
    def extract_from_topics(topics: List[str], repo_name: str) -> List[Dict]:
        evidence = []
        for topic in topics:
            evidence.append({
                "technology": topic,
                "source": "github",
                "evidence_type": "repository_topic",
                "repository": repo_name,
                "details": {"topic": topic},
            })
        return evidence

    @staticmethod
    def extract_from_dependency_file(
        file_content: str, filename: str, repo_name: str
    ) -> List[Dict]:
        evidence = []
        parser_name = DEPENDENCY_PARSERS.get(filename)
        if not parser_name:
            return evidence
        parser_fn = getattr(TechEvidenceExtractor, parser_name, None)
        if not parser_fn:
            return evidence
        deps = parser_fn(file_content)
        for dep in deps:
            evidence.append({
                "technology": dep,
                "source": "github",
                "evidence_type": "dependency",
                "repository": repo_name,
                "details": {"source_file": filename},
            })
        return evidence

    @staticmethod
    def extract_from_readme(readme_text: str, repo_name: str) -> List[Dict]:
        if not readme_text:
            return []
        tech_patterns = [
            r'\b(python|java|javascript|typescript|go|rust|c\+\+|ruby|php|swift|kotlin)\b',
            r'\b(docker|kubernetes|terraform|ansible|aws|azure|gcp)\b',
            r'\b(flask|django|fastapi|express|spring|react|vue|angular|next\.?js|node\.?js)\b',
            r'\b(postgresql|mysql|mongodb|redis|elasticsearch|sqlite)\b',
            r'\b(linux|bash|powershell|nginx|apache)\b',
            r'\b(splunk|wireshark|nmap|metasploit|burp|owasp)\b',
            r'\b(git|github|gitlab|jenkins|ci/cd|devops)\b',
        ]
        evidence = []
        seen = set()
        text_lower = readme_text.lower()
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for m in matches:
                m_lower = m.lower()
                if m_lower not in seen:
                    seen.add(m_lower)
                    evidence.append({
                        "technology": m.title(),
                        "source": "github",
                        "evidence_type": "readme_mention",
                        "repository": repo_name,
                        "details": {"source_file": "README.md"},
                    })
        return evidence

    @staticmethod
    def extract_all(
        languages: Dict[str, int],
        topics: List[str],
        repo_name: str,
        readme_text: Optional[str] = None,
        dependency_files: Optional[Dict[str, str]] = None,
    ) -> List[Dict]:
        all_evidence = []
        all_evidence.extend(TechEvidenceExtractor.extract_from_languages(languages, repo_name))
        all_evidence.extend(TechEvidenceExtractor.extract_from_topics(topics, repo_name))
        if readme_text:
            all_evidence.extend(TechEvidenceExtractor.extract_from_readme(readme_text, repo_name))
        if dependency_files:
            for filename, content in dependency_files.items():
                if content:
                    all_evidence.extend(
                        TechEvidenceExtractor.extract_from_dependency_file(content, filename, repo_name)
                    )
        return all_evidence

    @staticmethod
    def _parse_requirements_txt(content: str) -> List[str]:
        deps = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            name = re.split(r'[>=<!\[]', line)[0].strip()
            if name:
                deps.append(name)
        return deps

    @staticmethod
    def _parse_pyproject_toml(content: str) -> List[str]:
        deps = []
        in_deps = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("[") and "dependencies" in stripped:
                in_deps = True
                continue
            if stripped.startswith("[") and in_deps:
                in_deps = False
                continue
            if in_deps and stripped and not stripped.startswith("#"):
                match = re.match(r'"([^"]+)"', stripped.rstrip(","))
                if match:
                    name = re.split(r'[>=<!\[]', match.group(1))[0].strip()
                    if name:
                        deps.append(name)
        return deps

    @staticmethod
    def _parse_pipfile(content: str) -> List[str]:
        deps = []
        in_deps = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped == "[packages]":
                in_deps = True
                continue
            if stripped.startswith("[") and in_deps:
                in_deps = False
                continue
            if in_deps and stripped and not stripped.startswith("#"):
                match = re.match(r'([A-Za-z0-9_-]+)', stripped)
                if match:
                    deps.append(match.group(1))
        return deps

    @staticmethod
    def _parse_package_json(content: str) -> List[str]:
        try:
            data = json.loads(content)
            deps = list(data.get("dependencies", {}).keys())
            dev_deps = list(data.get("devDependencies", {}).keys())
            return deps + dev_deps
        except (json.JSONDecodeError, AttributeError):
            return []

    @staticmethod
    def _parse_pom_xml(content: str) -> List[str]:
        deps = []
        for match in re.finditer(r'<artifactId>([^<]+)</artifactId>', content):
            name = match.group(1).strip()
            if name and name not in ("maven", "parent"):
                deps.append(name)
        return deps

    @staticmethod
    def _parse_build_gradle(content: str) -> List[str]:
        deps = []
        for match in re.finditer(r"implementation\s+['\"]([^'\"]+)['\"]", content):
            parts = match.group(1).split(":")
            if len(parts) >= 2:
                deps.append(parts[1])
        return deps

    @staticmethod
    def _parse_go_mod(content: str) -> List[str]:
        deps = []
        in_require = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("require"):
                in_require = True
                stripped = stripped[len("require"):].strip().lstrip("(")
            if in_require and stripped == ")":
                in_require = False
                continue
            if in_require or stripped.startswith("require"):
                parts = stripped.split()
                if parts:
                    mod = parts[0].strip()
                    if "/" in mod:
                        name = mod.split("/")[-1]
                        deps.append(name)
        return deps
