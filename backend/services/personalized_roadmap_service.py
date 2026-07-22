import logging
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from knowledge.loader import knowledge_loader
from services.role_gap_analysis_service import RoleGapAnalysisService
from repositories.repositories import (
    RoadmapRepository,
    SkillEvidenceRepository,
    AssessmentRepository,
)

logger = logging.getLogger(__name__)

RESOURCE_URLS = {
    "Microsoft Learn": {"url": "https://learn.microsoft.com/en-us/windows/", "type": "course", "free": True},
    "Splunk Free Training": {"url": "https://www.splunk.com/en_us/training/free-online-training.html", "type": "course", "free": True},
    "Splunk Documentation": {"url": "https://docs.splunk.com/", "type": "article", "free": True},
    "Wireshark Documentation": {"url": "https://www.wireshark.org/docs/", "type": "article", "free": True},
    "Wireshark Wiki": {"url": "https://wiki.wireshark.org/", "type": "article", "free": True},
    "Cisco Skills for All": {"url": "https://skillsforall.com/", "type": "course", "free": True},
    "TryHackMe": {"url": "https://tryhackme.com/", "type": "lab", "free": True},
    "Hack The Box": {"url": "https://www.hackthebox.com/", "type": "lab", "free": True},
    "SANS DFIR": {"url": "https://www.sans.org/white-papers/incident-handling-process/", "type": "article", "free": True},
    "Automate the Boring Stuff": {"url": "https://automatetheboringstuff.com/", "type": "book", "free": True},
    "MITRE ATT&CK Website": {"url": "https://attack.mitre.org/", "type": "article", "free": True},
    "The Linux Command Line": {"url": "https://linuxcommand.org/tlcl.php", "type": "book", "free": True},
    "OverTheWire": {"url": "https://overthewire.org/wargames/bandit/", "type": "lab", "free": True},
    "Nmap Documentation": {"url": "https://nmap.org/docs.html", "type": "article", "free": True},
    "PortSwigger Web Security Academy": {"url": "https://portswigger.net/web-security", "type": "course", "free": True},
    "PortSwigger": {"url": "https://portswigger.net/web-security", "type": "course", "free": True},
    "DFIR Training": {"url": "https://www.dfir.training/", "type": "course", "free": True},
    "Kubernetes Documentation": {"url": "https://kubernetes.io/docs/home/", "type": "article", "free": True},
    "HashiCorp Learn": {"url": "https://developer.hashicorp.com/terraform/tutorials", "type": "course", "free": True},
    "AWS Documentation": {"url": "https://docs.aws.amazon.com/iam/", "type": "article", "free": True},
    "OWASP": {"url": "https://owasp.org/www-project-top-ten/", "type": "article", "free": True},
    "Splunk": {"url": "https://www.splunk.com/en_us/training/free-online-training.html", "type": "course", "free": True},
    "Wireshark": {"url": "https://www.wireshark.org/docs/", "type": "article", "free": True},
}

CERT_URLS = {
    "Google Cybersecurity Professional Certificate": "https://www.coursera.org/professional-certificates/google-cybersecurity",
    "CompTIA Security+": "https://www.comptia.org/certifications/security",
    "Blue Team Level 1": "https://securityblue.team/bugs/",
    "eJPT": "https://ine.com/certifications/ine-security-certified-endpoint-professional",
    "PNPT": "https://pntoacademy.com/pnpt",
    "OSCP": "https://www.offensive-security.com/pwk-oscp/",
    "AWS Security Specialty": "https://aws.amazon.com/certification/certified-security-specialty/",
    "CCSK": "https://cloudsecurityalliance.org/research/ccsk/",
    "Azure Security Engineer": "https://learn.microsoft.com/en-us/credentials/certifications/azure-security-engineer/",
    "CSSLP": "https://www.isc2.org/credentials/csslp",
    "GCFA": "https://www.giac.org/certifications/forensic-analyst-gcfa/",
    "CTIA": "https://cert.eccouncil.org/programs/cyber-threat-intelligence-ctia/",
    "GCTI": "https://www.giac.org/certifications/cyber-threat-intelligence-gcti/",
    "CISSP": "https://www.isc2.org/credentials/cissp",
    "CCSP": "https://www.isc2.org/credentials/ccsp",
    "Certified Kubernetes Security Specialist": "https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/",
    "GCIH": "https://www.giac.org/certifications/incident-handler-gcih/",
    "CISA": "https://www.isaca.org/credentials/cisa",
    "CRISC": "https://www.isaca.org/credentials/crisc",
    "ISO 27001 Lead Implementer": "https://pecb.com/en/education-and-certification-for-individuals/iso-27001-lead-implementer",
    "CEH": "https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/",
    "CompTIA CySA+": "https://www.comptia.org/certifications/cybersecurity-analyst",
    "OSWE": "https://www.offensive-security.com/awe-oswe/",
}

PROJECT_URLS = {
    "Port Scanner": {"github": "https://github.com/topics/port-scanner", "guide": "https://www.thepythoncode.com/article/write-a-port-scanner"},
    "Password Strength Checker": {"github": "https://github.com/topics/password-strength", "guide": "https://www.thepythoncode.com/article/make-a-password-strength-checker"},
    "Log Parser": {"github": "https://github.com/topics/log-analyzer", "guide": "https://www.linuxjournal.com/content/log-analysis-tools"},
    "Web Vulnerability Scanner": {"github": "https://github.com/topics/web-vulnerability-scanner", "guide": "https://portswigger.net/web-security"},
    "Network Monitoring Dashboard": {"github": "https://github.com/topics/network-monitoring", "guide": "https://docs.python.org/3/library/http.server.html"},
    "Secure REST API": {"github": "https://github.com/topics/secure-api", "guide": "https://fastapi.tiangolo.com/tutorial/security/"},
    "SIEM Home Lab": {"github": "https://github.com/topics/siem", "guide": "https://www.splunk.com/en_us/training/free-online-training.html"},
    "CI/CD Security Pipeline": {"github": "https://github.com/topics/ci-cd-security", "guide": "https://docs.github.com/en/actions/security-guides"},
    "Cloud Security Lab": {"github": "https://github.com/topics/aws-security", "guide": "https://docs.aws.amazon.com/security/"},
    "Active Directory Lab": {"github": "https://github.com/topics/active-directory", "guide": "https://www.thehackerrecipes.com/"},
    "Kubernetes Hardening": {"github": "https://github.com/topics/kubernetes-security", "guide": "https://kubernetes.io/docs/concepts/security/"},
    "Memory Investigation": {"github": "https://github.com/topics/volatility", "guide": "https://www.volatilityfoundation.org/"},
    "Vulnerability Scanner": {"github": "https://github.com/topics/vulnerability-scanner", "guide": "https://nmap.org/docs.html"},
    "Packet Capture Analyzer": {"github": "https://github.com/topics/packet-analysis", "guide": "https://www.wireshark.org/docs/"},
    "Threat Detection Dashboard": {"github": "https://github.com/topics/threat-detection", "guide": "https://attack.mitre.org/"},
    "API Security Testing Suite": {"github": "https://github.com/topics/api-security", "guide": "https://owasp.org/www-project-api-security/"},
    "Container Security Scanner": {"github": "https://github.com/topics/container-security", "guide": "https://docs.docker.com/engine/security/"},
    "Zero Trust Network Lab": {"github": "https://github.com/topics/zero-trust", "guide": "https://www.nist.gov/itl/applied-cybersecurity/zero-trust-architecture"},
    "Incident Response Playbook": {"github": "https://github.com/topics/incident-response", "guide": "https://www.nist.gov/itl/publications"},
    "Malware Analysis Sandbox": {"github": "https://github.com/topics/malware-analysis", "guide": "https://www.malwarebytes.com/resources"},
    "OSINT Recon Tool": {"github": "https://github.com/topics/osint", "guide": "https://osintframework.com/"},
    "SIEM Rule Generator": {"github": "https://github.com/topics/siem-rules", "guide": "https://attack.mitre.org/"},
    "Compliance Audit Framework": {"github": "https://github.com/topics/compliance", "guide": "https://pages.nist.gov/"},
    "Wireless Network Auditor": {"github": "https://github.com/topics/wireless-security", "guide": "https://www.aircrack-ng.org/doku.php"},
    "Phishing Detection Tool": {"github": "https://github.com/topics/phishing-detection", "guide": "https://www.phishtank.com/"},
    "Secrets Scanner": {"github": "https://github.com/topics/secret-scanning", "guide": "https://docs.github.com/en/code-security/secret-scanning"},
    "Threat Intelligence Feed Aggregator": {"github": "https://github.com/topics/threat-intelligence", "guide": "https://www.alienvault.com/open-threat-exchange"},
    "Forensics Timeline Tool": {"github": "https://github.com/topics/forensics", "guide": "https://www.sleuthkit.org/"},
    "IAM Policy Analyzer": {"github": "https://github.com/topics/iam", "guide": "https://docs.aws.amazon.com/IAM/latest/UserGuide/"},
    "DevSecOps Pipeline Dashboard": {"github": "https://github.com/topics/devsecops", "guide": "https://owasp.org/www-project-devsecops-guideline/"},
    "Compliance Gap Analysis": {"github": "https://github.com/topics/compliance", "guide": "https://www.nist.gov/itl/cybersecurity"},
    "Risk Register Framework": {"github": "https://github.com/topics/risk-management", "guide": "https://www.nist.gov/itl/publications"},
    "Policy Documentation Suite": {"github": "https://github.com/topics/security-policy", "guide": "https://www.sans.org/information-security-policy/"},
    "Tabletop Exercise": {"github": "https://github.com/topics/incident-response", "guide": "https://www.cisa.gov/topics/incident-response-planning"},
    "Threat Actor Profile": {"github": "https://github.com/topics/threat-intelligence", "guide": "https://attack.mitre.org/groups/"},
    "OSINT Investigation": {"github": "https://github.com/topics/osint", "guide": "https://osintframework.com/"},
    "Threat Feed Dashboard": {"github": "https://github.com/topics/threat-intelligence", "guide": "https://www.alienvault.com/open-threat-exchange"},
    "Malware Analysis Sandbox": {"github": "https://github.com/topics/malware-analysis", "guide": "https://www.malwarebytes.com/resources"},
    "Forensics Timeline Tool": {"github": "https://github.com/topics/forensics", "guide": "https://www.sleuthkit.org/"},
}


class PersonalizedRoadmapService:
    """
    Evidence-driven personalized career roadmap engine.
    
    Generates dependency-aware, evidence-aware, personalized, explainable,
    progress-trackable, and recalculable roadmaps from user skill evidence,
    skill gaps, target role requirements, and prerequisite dependencies.
    
    The deterministic engine owns:
    - Skill ordering (topological sort)
    - Prerequisite resolution
    - Gap prioritization
    - Project/certification placement
    - Dependency validation
    - Roadmap validity
    
    AI may only assist with:
    - Explanations and descriptions
    - Motivation and personalization
    - Phase naming
    NEVER: reorder dependencies, invent prerequisites, or change skill ordering.
    """

    def __init__(self):
        self.kb = knowledge_loader
        self.roadmap_repo = RoadmapRepository()
        self.evidence_repo = SkillEvidenceRepository()
        self.assessment_repo = AssessmentRepository()
        self.gap_service = RoleGapAnalysisService()

    def generate_roadmap(
        self,
        user_id: str,
        assessment_id: str,
        role_id: str,
        weekly_hours: int = 10,
        learning_style: str = "hands-on",
        generation_reason: str = "initial",
    ) -> Dict[str, Any]:
        """
        Generate a personalized roadmap for a user targeting a specific role.
        
        Args:
            user_id: The user's ID
            assessment_id: The assessment ID linking to career analysis
            role_id: The target role ID
            weekly_hours: Available study hours per week
            learning_style: User's preferred learning style
            generation_reason: Why this roadmap was generated
            
        Returns:
            Complete roadmap data with nodes, phases, metadata
        """
        logger.info("Generating roadmap for user=%s role=%s", user_id, role_id)

        # 1. Load role data
        role_data = self.kb.get_role(role_id)
        if not role_data:
            logger.error("Role not found: %s", role_id)
            return {"error": f"Role '{role_id}' not found"}

        # 2. Load user skill evidence (confidences)
        skill_confidences = self._load_skill_confidences(user_id)

        # 3. Calculate gap analysis
        gap_analysis = self.gap_service.analyze_role_gap(user_id, role_id)
        if "error" in gap_analysis:
            return gap_analysis

        # 4. Build dependency graph for role
        dependency_graph = self._build_dependency_graph(role_data)

        # 5. Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(dependency_graph)
        if circular_deps:
            logger.warning("Circular dependencies detected: %s", circular_deps)

        # 6. Determine required learning set (skills user needs to learn)
        required_learning = self._determine_required_learning(
            role_data, skill_confidences, dependency_graph
        )

        # 7. Topological sort with evidence awareness
        sorted_skills = self._topological_sort_with_evidence(
            required_learning, dependency_graph, skill_confidences
        )

        # 8. Create skill nodes
        skill_nodes = self._create_skill_nodes(
            sorted_skills, skill_confidences, dependency_graph
        )

        # 9. Select and place projects
        project_nodes = self._select_and_place_projects(
            skill_nodes, role_data, skill_confidences, learning_style
        )

        # 10. Place certifications
        cert_nodes = self._place_certifications(
            skill_nodes, role_data, skill_confidences
        )

        # 11. Merge all nodes in dependency order
        all_nodes = self._merge_nodes_in_order(skill_nodes, project_nodes, cert_nodes)

        # 12. Group into meaningful phases
        phases = self._group_into_phases(all_nodes, role_data)

        # 13. Assign status to each node
        all_nodes = self._assign_node_statuses(all_nodes, skill_confidences)

        # 14. Calculate totals
        total_hours = sum(n.get("estimatedHours", 0) for n in all_nodes)
        estimated_weeks = max(1, total_hours // max(1, weekly_hours))

        # 15. Get current readiness
        readiness_score = int(gap_analysis.get("readiness_score", 0) * 100)

        # 16. Save to database
        version = 1
        existing = self.roadmap_repo.get_latest_by_user_and_assessment(user_id, assessment_id)
        if existing:
            version = existing.version + 1

        roadmap_record = self.roadmap_repo.create(
            assessment_id=assessment_id,
            steps=all_nodes,
            total_hours=total_hours,
            estimated_weeks=estimated_weeks,
            user_id=user_id,
            version=version,
            generation_reason=generation_reason,
            readiness_score_at_creation=readiness_score,
            phases=phases,
        )

        return {
            "roadmap_id": str(roadmap_record.id),
            "version": version,
            "user_id": user_id,
            "assessment_id": assessment_id,
            "role_id": role_id,
            "role_name": role_data.get("role", role_id),
            "nodes": all_nodes,
            "phases": phases,
            "total_hours": total_hours,
            "estimated_weeks": estimated_weeks,
            "readiness_score": readiness_score,
            "generation_reason": generation_reason,
            "created_at": roadmap_record.created_at.isoformat() if roadmap_record.created_at else None,
        }

    def regenerate_roadmap(
        self,
        user_id: str,
        assessment_id: str,
        role_id: str,
        weekly_hours: int = 10,
        learning_style: str = "hands-on",
        preserve_completed: bool = True,
    ) -> Dict[str, Any]:
        """
        Regenerate roadmap when new evidence appears.
        Preserves completed progress from previous version.
        """
        previous = self.roadmap_repo.get_latest_by_user_and_assessment(user_id, assessment_id)
        completed_nodes = set()
        if previous and preserve_completed:
            for node in (previous.steps or []):
                if node.get("status") == "completed":
                    completed_nodes.add(node.get("id") or node.get("title", ""))

        result = self.generate_roadmap(
            user_id=user_id,
            assessment_id=assessment_id,
            role_id=role_id,
            weekly_hours=weekly_hours,
            learning_style=learning_style,
            generation_reason="recalculation",
        )

        if "error" not in result and preserve_completed and completed_nodes:
            for node in result.get("nodes", []):
                node_id = node.get("id") or node.get("title", "")
                if node_id in completed_nodes:
                    node["status"] = "completed"
                    node["completedAt"] = datetime.utcnow().isoformat()

        return result

    def get_user_roadmap(self, user_id: str, assessment_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the latest roadmap for a user."""
        if assessment_id:
            roadmap = self.roadmap_repo.get_latest_by_user_and_assessment(user_id, assessment_id)
        else:
            roadmaps = self.roadmap_repo.get_by_user_id(user_id, limit=1)
            roadmap = roadmaps[0] if roadmaps else None

        if not roadmap:
            return None

        return {
            "roadmap_id": str(roadmap.id),
            "version": roadmap.version,
            "user_id": str(roadmap.user_id),
            "assessment_id": str(roadmap.assessment_id),
            "nodes": roadmap.steps or [],
            "phases": roadmap.phases or [],
            "total_hours": roadmap.total_hours,
            "estimated_weeks": roadmap.estimated_weeks,
            "readiness_score": roadmap.readiness_score_at_creation,
            "generation_reason": roadmap.generation_reason,
            "created_at": roadmap.created_at.isoformat() if roadmap.created_at else None,
        }

    def toggle_node_status(self, roadmap_id: str, node_index: int) -> Dict[str, Any]:
        """Toggle a roadmap node's status following the locked->available->in-progress->completed logic."""
        from database.session import SessionLocal
        from models.sqlalchemy_models import Roadmap

        db = SessionLocal()
        try:
            roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
            if not roadmap:
                return {"error": "Roadmap not found"}

            nodes = list(roadmap.steps or [])
            if node_index < 0 or node_index >= len(nodes):
                return {"error": "Invalid node index"}

            node = nodes[node_index]
            current_status = node.get("status", "locked")

            if current_status == "locked":
                return {"error": "Cannot toggle a locked node"}
            elif current_status == "available":
                node["status"] = "in-progress"
            elif current_status == "in-progress":
                node["status"] = "completed"
                node["completedAt"] = datetime.utcnow().isoformat()
                self._unlock_dependents(nodes, node_index)
            elif current_status == "completed":
                node["status"] = "in-progress"
                node["completedAt"] = None

            nodes[node_index] = node
            roadmap.steps = nodes
            db.commit()
            db.refresh(roadmap)

            return {
                "roadmap_id": str(roadmap.id),
                "nodes": roadmap.steps,
                "updated_node": node,
            }
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # Private helper methods
    # -------------------------------------------------------------------------

    def _load_skill_confidences(self, user_id: str) -> Dict[str, float]:
        """Load user skill confidences from evidence repository."""
        evidences = self.evidence_repo.get_by_user_id(user_id)
        if not evidences:
            return {}

        confidences = {}
        for ev in evidences:
            skill_id = ev.skill_id if hasattr(ev, "skill_id") else ev.skill_name
            confidence = ev.confidence / 100.0 if hasattr(ev, "confidence") and ev.confidence else 0.0
            confidences[skill_id] = confidence

        return confidences

    def _build_dependency_graph(self, role_data: Dict) -> Dict[str, List[str]]:
        """
        Build dependency graph from role required skills + all their prerequisites.
        Returns adjacency list: skill -> list of prerequisites.
        """
        required_skills = role_data.get("required_skills", [])
        graph = {}
        visited = set()
        queue = list(required_skills)

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            skill_data = self.kb.get_skill(current)
            if skill_data:
                prereqs = skill_data.get("prerequisites", [])
                graph[current] = prereqs
                for p in prereqs:
                    if p not in visited:
                        queue.append(p)
            else:
                graph[current] = []

        return graph

    def _detect_circular_dependencies(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for prereq in graph.get(node, []):
                if prereq not in visited:
                    result = dfs(prereq, list(path))
                    if result:
                        return result
                elif prereq in rec_stack:
                    cycle_start = path.index(prereq)
                    return path[cycle_start:] + [prereq]

            rec_stack.remove(node)
            return None

        for node in graph:
            if node not in visited:
                cycle = dfs(node, [])
                if cycle:
                    cycles.append(cycle)

        return cycles

    def _determine_required_learning(
        self,
        role_data: Dict,
        skill_confidences: Dict[str, float],
        dependency_graph: Dict[str, List[str]],
    ) -> Set[str]:
        """
        Determine the set of skills the user needs to learn.
        Includes:
        - Required role skills with insufficient confidence
        - All prerequisites for those skills (recursive)
        """
        required_skills = role_data.get("required_skills", [])
        minimum_confidence_threshold = 0.6

        required_learning = set()
        queue = list(required_skills)

        while queue:
            current = queue.pop(0)
            if current in required_learning:
                continue

            confidence = skill_confidences.get(current, 0.0)
            if confidence < minimum_confidence_threshold:
                required_learning.add(current)
                for prereq in dependency_graph.get(current, []):
                    if prereq not in required_learning:
                        queue.append(prereq)

        return required_learning

    def _topological_sort_with_evidence(
        self,
        required_learning: Set[str],
        dependency_graph: Dict[str, List[str]],
        skill_confidences: Dict[str, float],
    ) -> List[str]:
        """
        Topologically sort required learning skills.
        Skills with higher confidence are placed later (reinforcement).
        Skills needed as prerequisites come first.
        """
        in_degree = {node: 0 for node in required_learning}
        for node in required_learning:
            for prereq in dependency_graph.get(node, []):
                if prereq in required_learning:
                    in_degree[node] += 1

        queue = []
        for node in required_learning:
            if in_degree[node] == 0:
                confidence = skill_confidences.get(node, 0.0)
                queue.append((confidence, node))

        queue.sort(key=lambda x: x[0])

        sorted_skills = []
        visited = set()

        while queue:
            _, current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            sorted_skills.append(current)

            for node in required_learning:
                if current in dependency_graph.get(node, []):
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        confidence = skill_confidences.get(node, 0.0)
                        queue.append((confidence, node))
                        queue.sort(key=lambda x: x[0])

        return sorted_skills

    def _create_skill_nodes(
        self,
        sorted_skills: List[str],
        skill_confidences: Dict[str, float],
        dependency_graph: Dict[str, List[str]],
    ) -> List[Dict[str, Any]]:
        """Create roadmap nodes for each skill in topological order."""
        nodes = []
        for i, skill_name in enumerate(sorted_skills):
            skill_data = self.kb.get_skill(skill_name) or {
                "name": skill_name,
                "category": "General",
                "difficulty": "beginner",
                "estimated_hours": 10,
                "prerequisites": [],
                "learning_resources": [],
            }

            hours = skill_data.get("estimated_hours", 10)
            difficulty = skill_data.get("difficulty", "beginner")
            prerequisites = dependency_graph.get(skill_name, [])
            confidence = skill_confidences.get(skill_name, 0.0)

            resources = []
            for j, r in enumerate(skill_data.get("learning_resources", [])):
                if isinstance(r, str):
                    meta = RESOURCE_URLS.get(r, {})
                    resources.append({
                        "id": f"res-{i}-{j}",
                        "title": r,
                        "type": meta.get("type", "article"),
                        "url": meta.get("url", "#"),
                        "free": meta.get("free", True),
                    })

            nodes.append({
                "id": f"skill-{skill_name.lower().replace(' ', '-')}",
                "title": skill_name,
                "description": f"Learn {skill_name} - {skill_data.get('category', 'Cybersecurity')}",
                "type": "skill",
                "status": "locked",
                "estimatedHours": hours,
                "difficulty": difficulty.capitalize() if difficulty else "Beginner",
                "skills": [skill_name],
                "prerequisites": [f"skill-{p.lower().replace(' ', '-')}" for p in prerequisites],
                "resources": resources,
                "confidence": confidence,
            })

        return nodes

    def _select_and_place_projects(
        self,
        skill_nodes: List[Dict],
        role_data: Dict,
        skill_confidences: Dict[str, float],
        learning_style: str,
    ) -> List[Dict[str, Any]]:
        """
        Select projects that:
        1. Target priority gaps
        2. Reuse existing strengths
        3. Produce portfolio artifacts
        4. Align with target role
        """
        role_name = role_data.get("role", "")
        suggested_project_titles = role_data.get("suggested_projects", [])
        all_projects = {p["title"]: p for p in self.kb.get_projects()}

        skill_titles = {n["title"].lower() for n in skill_nodes}
        project_nodes = []

        for proj_title in suggested_project_titles:
            proj_data = all_projects.get(proj_title)
            if not proj_data:
                for t, p in all_projects.items():
                    if proj_title.lower() in t.lower() or t.lower() in proj_title.lower():
                        proj_data = p
                        break
            if not proj_data:
                continue

            proj_skills = [s.lower() for s in proj_data.get("skills", [])]
            last_skill_idx = -1
            for ps in proj_skills:
                for idx, sn in enumerate(skill_nodes):
                    if ps == sn["title"].lower():
                        last_skill_idx = max(last_skill_idx, idx)

            if last_skill_idx == -1:
                continue

            urls = PROJECT_URLS.get(proj_data["title"], {})
            project_nodes.append({
                "insert_after": last_skill_idx,
                "node": {
                    "id": f"proj-{proj_data['title'].lower().replace(' ', '-')}",
                    "title": proj_data["title"],
                    "description": f"Hands-on project: {proj_data['title']}. Build {', '.join(proj_data.get('skills', [])[:3])} skills with real deliverables.",
                    "type": "project",
                    "status": "locked",
                    "estimatedHours": proj_data.get("estimated_hours", 10),
                    "difficulty": proj_data.get("difficulty", "Medium"),
                    "skills": proj_data.get("skills", []),
                    "prerequisites": [],
                    "resources": [
                        {
                            "id": f"proj-res-{proj_data['title'].lower().replace(' ', '-')}-gh",
                            "title": "GitHub Starter Template",
                            "type": "lab",
                            "url": urls.get("github", "#"),
                            "free": True,
                        },
                        {
                            "id": f"proj-res-{proj_data['title'].lower().replace(' ', '-')}-guide",
                            "title": "Implementation Guide",
                            "type": "course",
                            "url": urls.get("guide", "#"),
                            "free": True,
                        },
                    ],
                },
            })

        return project_nodes

    def _place_certifications(
        self,
        skill_nodes: List[Dict],
        role_data: Dict,
        skill_confidences: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """
        Place certifications only after prerequisite skills are sufficiently developed.
        """
        role_name = role_data.get("role", "")
        certs = self.kb.get_certifications_for_role(role_name)
        if not certs:
            canonical = self.kb.ROLE_ALIASES.get(role_name.lower(), role_name)
            certs = self.kb.get_certifications_for_role(canonical)

        skill_names_in_roadmap = {n["title"].lower() for n in skill_nodes}
        cert_nodes = []

        for cert in certs:
            cert_prereqs = [p.lower() for p in cert.get("prerequisites", [])]
            if cert_prereqs and not any(p in skill_names_in_roadmap for p in cert_prereqs):
                continue

            last_prereq_idx = len(skill_nodes) - 1
            if cert_prereqs:
                for p in cert_prereqs:
                    for idx, sn in enumerate(skill_nodes):
                        if p == sn["title"].lower():
                            last_prereq_idx = max(last_prereq_idx, idx)

            cert_url = CERT_URLS.get(cert["name"], "#")
            cert_nodes.append({
                "insert_after": last_prereq_idx,
                "node": {
                    "id": f"cert-{cert['name'].lower().replace(' ', '-')}",
                    "title": cert["name"],
                    "description": f"{cert['vendor']} certification. Difficulty: {cert['difficulty']}.",
                    "type": "certification",
                    "status": "locked",
                    "estimatedHours": 40,
                    "difficulty": cert["difficulty"].capitalize() if cert["difficulty"] else "Beginner",
                    "skills": [cert["name"]],
                    "prerequisites": [f"skill-{p.lower().replace(' ', '-')}" for p in cert.get("prerequisites", [])],
                    "resources": [{
                        "id": f"cert-res-{cert['name'].lower().replace(' ', '-')}",
                        "title": cert["name"],
                        "type": "course",
                        "url": cert_url,
                        "free": False,
                    }],
                },
            })

        return cert_nodes

    def _merge_nodes_in_order(
        self,
        skill_nodes: List[Dict],
        project_nodes: List[Dict],
        cert_nodes: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Merge skill, project, and certification nodes in dependency order."""
        all_nodes = list(skill_nodes)

        project_nodes.sort(key=lambda p: p["insert_after"])
        offset = 0
        for pn in project_nodes:
            insert_at = pn["insert_after"] + offset + 1
            all_nodes.insert(insert_at, pn["node"])
            offset += 1

        cert_nodes.sort(key=lambda c: c["insert_after"])
        offset = 0
        for cn in cert_nodes:
            insert_at = cn["insert_after"] + offset + 1
            all_nodes.insert(insert_at, cn["node"])
            offset += 1

        for idx, node in enumerate(all_nodes):
            node["id"] = f"step-{idx}"

        return all_nodes

    def _group_into_phases(self, nodes: List[Dict], role_data: Dict) -> List[Dict[str, Any]]:
        """
        Group roadmap nodes into meaningful learning phases.
        Phases are based on skill categories and difficulty progression.
        """
        phases = []
        current_phase = None
        node_idx = 0

        category_groups = defaultdict(list)
        for node in nodes:
            if node.get("type") == "skill":
                skill_data = self.kb.get_skill(node["title"])
                category = skill_data.get("category", "General") if skill_data else "General"
                category_groups[category].append(node)
            else:
                category_groups["Projects & Certifications"].append(node)

        phase_order = [
            "Operating Systems",
            "Networking",
            "Programming",
            "Defensive Security",
            "Offensive Security",
            "Web Security",
            "Cloud",
            "Digital Forensics",
            "Application Security",
            "DevOps",
            "Governance",
            "Projects & Certifications",
        ]

        phase_number = 1
        for category in phase_order:
            if category not in category_groups:
                continue

            category_nodes = category_groups[category]
            if not category_nodes:
                continue

            total_hours = sum(n.get("estimatedHours", 0) for n in category_nodes)
            skill_count = sum(1 for n in category_nodes if n.get("type") == "skill")
            project_count = sum(1 for n in category_nodes if n.get("type") == "project")
            cert_count = sum(1 for n in category_nodes if n.get("type") == "certification")

            phases.append({
                "id": f"phase-{phase_number}",
                "name": f"Phase {phase_number}: {category}",
                "description": f"Master {category.lower()} concepts and skills",
                "nodeRange": [node_idx, node_idx + len(category_nodes) - 1],
                "totalHours": total_hours,
                "skillCount": skill_count,
                "projectCount": project_count,
                "certificationCount": cert_count,
            })
            node_idx += len(category_nodes)
            phase_number += 1

        return phases

    def _assign_node_statuses(
        self,
        nodes: List[Dict],
        skill_confidences: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """
        Assign status to each node based on dependency satisfaction.
        Status logic: locked -> available -> in-progress -> completed
        """
        completed_skills = set()
        for node in nodes:
            if node.get("status") == "completed":
                for skill in node.get("skills", []):
                    completed_skills.add(skill.lower())

        for node in nodes:
            if node.get("status") == "completed":
                continue

            prerequisites = node.get("prerequisites", [])
            all_prereqs_met = True
            for prereq_id in prerequisites:
                prereq_node = next((n for n in nodes if n.get("id") == prereq_id), None)
                if prereq_node and prereq_node.get("status") != "completed":
                    all_prereqs_met = False
                    break

            if all_prereqs_met:
                if node.get("type") == "skill":
                    skill_name = node.get("title", "")
                    confidence = skill_confidences.get(skill_name, 0.0)
                    if confidence >= 0.6:
                        node["status"] = "completed"
                    elif confidence > 0:
                        node["status"] = "in-progress"
                    else:
                        node["status"] = "available"
                else:
                    node["status"] = "available"
            else:
                node["status"] = "locked"

        return nodes

    def _unlock_dependents(self, nodes: List[Dict], completed_index: int):
        """Unlock nodes that depend on the completed node."""
        completed_node = nodes[completed_index]
        completed_id = completed_node.get("id", "")

        for node in nodes:
            if node.get("status") == "locked":
                prerequisites = node.get("prerequisites", [])
                all_met = True
                for prereq_id in prerequisites:
                    if prereq_id == completed_id:
                        continue
                    prereq_node = next((n for n in nodes if n.get("id") == prereq_id), None)
                    if prereq_node and prereq_node.get("status") != "completed":
                        all_met = False
                        break
                if all_met:
                    node["status"] = "available"


personalized_roadmap_service = PersonalizedRoadmapService()
