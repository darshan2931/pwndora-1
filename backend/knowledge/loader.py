import json
from pathlib import Path
from typing import Dict, List, Optional

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge" / "versions" / "v1" / "current"


class KnowledgeLoader:
    def __init__(self, knowledge_dir: Path = KNOWLEDGE_DIR):
        self.knowledge_dir = knowledge_dir
        self._cache: Dict[str, list] = {}

    def _load(self, filename: str) -> list:
        if filename in self._cache:
            return self._cache[filename]
        filepath = self.knowledge_dir / filename
        if not filepath.exists():
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._cache[filename] = data
        return data

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


knowledge_loader = KnowledgeLoader()
