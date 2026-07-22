import logging
from typing import Any, Dict, List, Optional, Set
from collections import deque

from knowledge.loader import KnowledgeLoader

logger = logging.getLogger(__name__)


class ImpactAnalysis:
    def __init__(self, knowledge_loader: Optional[KnowledgeLoader] = None):
        self._knowledge_loader = knowledge_loader or KnowledgeLoader()
        self._dependency_graph: Dict[str, List[str]] = {}
        self._reverse_graph: Dict[str, List[str]] = {}
        self._loaded = False

    def _ensure_loaded(self):
        if self._loaded:
            return
        skills_raw = self._knowledge_loader.get_skills() or []
        for skill in skills_raw:
            name = skill.get("name", "")
            prereqs = skill.get("prerequisites", [])
            self._dependency_graph[name] = prereqs
            for prereq in prereqs:
                self._reverse_graph.setdefault(prereq, []).append(name)
        self._loaded = True

    def get_impacted_skills(self, changed_skill: str) -> List[str]:
        self._ensure_loaded()
        impacted: Set[str] = set()
        queue = deque([changed_skill])
        visited = {changed_skill}
        while queue:
            current = queue.popleft()
            dependents = self._reverse_graph.get(current, [])
            for dep in dependents:
                if dep not in visited:
                    visited.add(dep)
                    impacted.add(dep)
                    queue.append(dep)
        return sorted(impacted)

    def get_prerequisite_chain(self, skill_name: str) -> List[str]:
        self._ensure_loaded()
        chain: List[str] = []
        visited: Set[str] = set()
        stack = [skill_name]
        while stack:
            current = stack[-1]
            if current in visited:
                stack.pop()
                continue
            prereqs = self._dependency_graph.get(current, [])
            unmet = [p for p in prereqs if p not in visited]
            if not unmet:
                visited.add(current)
                chain.append(current)
                stack.pop()
            else:
                for p in unmet:
                    if p not in visited:
                        stack.append(p)
        return chain

    def get_impacted_roles(self, changed_skill: str) -> List[str]:
        self._ensure_loaded()
        try:
            from services.role_gap_config import ROLE_SKILL_CONFIGS
            impacted = []
            for role_id, config in ROLE_SKILL_CONFIGS.items():
                required = set(config.get("required_skills", {}).keys())
                optional = set(config.get("optional_skills", {}).keys())
                if changed_skill in required or changed_skill in optional:
                    impacted.append(role_id)
            return impacted
        except ImportError:
            return []

    def get_evidence_strength_for_event(self, event_type: str) -> Dict[str, Any]:
        strengths = {
            "roadmap_skill_completed": {"evidence_type": "learning_completion", "base_strength": 0.20},
            "roadmap_project_completed": {"evidence_type": "project_completion", "base_strength": 0.75},
            "roadmap_certification_completed": {"evidence_type": "certification_completion", "base_strength": 0.80},
            "github_repository_linked": {"evidence_type": "github_analysis", "base_strength": 0.60},
            "github_repository_analyzed": {"evidence_type": "github_analysis", "base_strength": 0.55},
            "github_profile_reanalyzed": {"evidence_type": "github_analysis", "base_strength": 0.50},
            "assessment_completed": {"evidence_type": "assessment", "base_strength": 0.50},
            "resume_uploaded": {"evidence_type": "resume", "base_strength": 0.50},
            "certification_added": {"evidence_type": "certification", "base_strength": 0.80},
            "experience_added": {"evidence_type": "experience", "base_strength": 0.65},
        }
        return strengths.get(event_type, {"evidence_type": "unknown", "base_strength": 0.30})
