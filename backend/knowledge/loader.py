import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "knowledge" / "versions" / "v1" / "current"

CACHE_TTL = 300

REQUIRED_FIELDS = {
    "roles.json": ["role", "description", "required_skills"],
    "skills.json": ["name", "category", "difficulty"],
    "projects.json": ["title", "difficulty", "skills", "estimated_hours"],
    "certifications.json": ["name", "vendor", "difficulty", "recommended_for"],
    "learning_paths.json": ["career", "sequence"],
}

VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
VALID_PROJECT_DIFFICULTIES = {"Easy", "Medium", "Hard"}
VALID_CATEGORIES = {
    "Operating Systems", "Networking", "Programming", "Web Security",
    "Cloud", "Defensive Security", "Offensive Security",
    "Digital Forensics", "Application Security", "DevOps",
}


class KnowledgeLoader:
    def __init__(self, knowledge_dir: Path = KNOWLEDGE_DIR):
        self.knowledge_dir = knowledge_dir
        self._cache: Dict[str, list] = {}

    def _load(self, filename: str) -> list:
        if filename in self._cache:
            data, ts = self._cache[filename]
            if time.time() - ts < CACHE_TTL:
                return data
            del self._cache[filename]
        filepath = self.knowledge_dir / filename
        if not filepath.exists():
            logger.warning("Knowledge file not found: %s", filepath)
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in %s: %s", filepath, e)
            return []
        if not isinstance(data, list):
            logger.error("Expected list in %s, got %s", filepath, type(data).__name__)
            return []
        self._cache[filename] = (data, time.time())
        return data

    def invalidate_cache(self, filename: str = None):
        if filename:
            self._cache.pop(filename, None)
        else:
            self._cache.clear()

    def get_roles(self) -> list:
        return self._load("roles.json")

    def get_skills(self) -> list:
        return self._load("skills.json")

    def get_projects(self) -> list:
        return self._load("projects.json")

    def get_certifications(self) -> list:
        return self._load("certifications.json")

    def get_learning_paths(self) -> list:
        return self._load("learning_paths.json")

    def get_role(self, role_name: str) -> Optional[dict]:
        for role in self.get_roles():
            if role.get("role", "").lower() == role_name.lower():
                return role
        return None

    def get_skill(self, skill_name: str) -> Optional[dict]:
        for skill in self.get_skills():
            if skill.get("name", "").lower() == skill_name.lower():
                return skill
        return None

    def get_projects_for_skill(self, skill_name: str) -> List[dict]:
        return [
            p for p in self.get_projects()
            if skill_name in p.get("skills", [])
        ]

    def get_certifications_for_role(self, role_name: str) -> List[dict]:
        return [
            c for c in self.get_certifications()
            if role_name in c.get("recommended_for", [])
        ]

    def get_learning_path(self, career: str) -> Optional[dict]:
        for path in self.get_learning_paths():
            if path.get("career", "").lower() == career.lower():
                return path
        return None

    def get_skill_prerequisites(self, skill_name: str) -> List[str]:
        skill = self.get_skill(skill_name)
        if skill:
            return skill.get("prerequisites", [])
        return []

    def get_skill_by_category(self, category: str) -> List[dict]:
        return [
            s for s in self.get_skills()
            if s.get("category", "").lower() == category.lower()
        ]

    def search_skills(self, query: str) -> List[dict]:
        query_lower = query.lower()
        return [
            s for s in self.get_skills()
            if query_lower in s.get("name", "").lower()
            or query_lower in s.get("category", "").lower()
        ]

    def validate_all(self) -> List[str]:
        errors = []
        for filename, required_fields in REQUIRED_FIELDS.items():
            data = self._load(filename)
            if not data:
                errors.append(f"{filename}: file missing or empty")
                continue
            for i, item in enumerate(data):
                for field in required_fields:
                    if field not in item:
                        errors.append(f"{filename}[{i}]: missing required field '{field}'")
                if filename == "skills.json":
                    diff = item.get("difficulty", "")
                    if diff and diff not in VALID_DIFFICULTIES:
                        errors.append(
                            f"{filename}[{i}] '{item.get('name')}': invalid difficulty '{diff}'"
                        )
                    cat = item.get("category", "")
                    if cat and cat not in VALID_CATEGORIES:
                        errors.append(
                            f"{filename}[{i}] '{item.get('name')}': invalid category '{cat}'"
                        )
                if filename == "projects.json":
                    diff = item.get("difficulty", "")
                    if diff and diff not in VALID_PROJECT_DIFFICULTIES:
                        errors.append(
                            f"{filename}[{i}] '{item.get('title')}': invalid difficulty '{diff}'"
                        )
        all_skill_names = {s["name"].lower() for s in self.get_skills()}
        all_role_names = {r["role"].lower() for r in self.get_roles()}
        for i, role in enumerate(self.get_roles()):
            for skill_name in role.get("required_skills", []) + role.get("optional_skills", []):
                if skill_name.lower() not in all_skill_names:
                    errors.append(f"roles.json[{i}] '{role['role']}': references unknown skill '{skill_name}'")
            for cert_name in role.get("recommended_certifications", []):
                cert_names = {c["name"].lower() for c in self.get_certifications()}
                if cert_name.lower() not in cert_names:
                    errors.append(f"roles.json[{i}] '{role['role']}': references unknown cert '{cert_name}'")
        for i, skill in enumerate(self.get_skills()):
            for prereq in skill.get("prerequisites", []):
                if prereq.lower() not in all_skill_names:
                    errors.append(f"skills.json[{i}] '{skill['name']}': references unknown prerequisite '{prereq}'")
        for i, path in enumerate(self.get_learning_paths()):
            if path.get("career", "").lower() not in all_role_names:
                errors.append(f"learning_paths.json[{i}]: references unknown career '{path.get('career')}'")
        return errors


knowledge_loader = KnowledgeLoader()
