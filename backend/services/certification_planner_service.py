import logging
from typing import Dict, List, Optional

from knowledge.loader import knowledge_loader

logger = logging.getLogger(__name__)

DIFFICULTY_MULTIPLIER = {
    "beginner": 1.0,
    "intermediate": 1.15,
    "advanced": 1.3,
}


class CertificationPlannerService:
    """Builds a personalized certification timeline and cost estimate.

    Timeline is computed from the knowledge-base study_hours per cert,
    scaled by difficulty, and divided by the user's weekly study hours.
    Certifications are sequenced by prerequisite order.
    """

    def __init__(self):
        self.kb = knowledge_loader

    def _resolve_chain(self, cert: dict, seen: Optional[set] = None) -> List[str]:
        """Return ordered prerequisite certification names for a cert."""
        seen = seen or set()
        chain = []
        for prereq in cert.get("prerequisites", []):
            prereq_cert = self.kb.get_certification(prereq)
            if prereq_cert and prereq_cert["name"] not in seen:
                seen.add(prereq_cert["name"])
                chain.extend(self._resolve_chain(prereq_cert, seen))
                chain.append(prereq_cert["name"])
        return chain

    def _effective_study_hours(self, cert: dict) -> float:
        base = float(cert.get("study_hours", 60) or 60)
        multiplier = DIFFICULTY_MULTIPLIER.get(cert.get("difficulty", "intermediate"), 1.15)
        return round(base * multiplier)

    def _cost(self, cert: dict) -> Dict[str, float]:
        return {
            "exam_cost": float(cert.get("exam_cost", 0) or 0),
            "training_cost": float(cert.get("training_cost", 0) or 0),
            "renewal_cost": float(cert.get("renewal_cost", 0) or 0),
            "total": float(cert.get("exam_cost", 0) or 0)
            + float(cert.get("training_cost", 0) or 0)
            + float(cert.get("renewal_cost", 0) or 0),
        }

    def build_plan(
        self,
        career_goal: str,
        study_hours_per_week: float = 10.0,
        completed_certifications: Optional[List[str]] = None,
    ) -> Dict:
        completed = [c.strip().lower() for c in (completed_certifications or [])]
        try:
            weekly = float(study_hours_per_week)
        except (TypeError, ValueError):
            weekly = 10.0
        weekly = max(1.0, weekly)

        role = self.kb.get_role(career_goal)
        if not role:
            logger.warning("Unknown career goal for cert planner: %s", career_goal)
            return {
                "career": career_goal,
                "certifications": [],
                "summary": {
                    "total_certifications": 0,
                    "total_weeks": 0,
                    "total_months": 0,
                    "total_cost": 0.0,
                    "weekly_study_hours": weekly,
                },
            }

        certs = [self.kb.get_certification(c) for c in role.get("recommended_certifications", [])]
        certs = [c for c in certs if c and c["name"].lower() not in completed]

        # Build prerequisite chains to surface missing certs
        expanded: Dict[str, dict] = {}
        for cert in certs:
            expanded[cert["name"]] = cert
            for prereq_name in self._resolve_chain(cert):
                prereq_cert = self.kb.get_certification(prereq_name)
                if prereq_cert and prereq_cert["name"].lower() not in completed:
                    expanded[prereq_cert["name"]] = prereq_cert

        ordered = self._order_by_prerequisites(list(expanded.values()))

        plan_items = []
        cumulative_weeks = 0.0
        for idx, cert in enumerate(ordered):
            study_hours = self._effective_study_hours(cert)
            weeks = round(study_hours / weekly, 1)
            cumulative_weeks += weeks
            plan_items.append(
                {
                    "position": idx + 1,
                    "name": cert["name"],
                    "vendor": cert.get("vendor", ""),
                    "difficulty": cert.get("difficulty", "intermediate"),
                    "prerequisites": cert.get("prerequisites", []),
                    "recommended": cert["name"].lower() in [c["name"].lower() for c in certs],
                    "study_hours": study_hours,
                    "weeks": weeks,
                    "start_week": round(cumulative_weeks - weeks, 1),
                    "end_week": round(cumulative_weeks, 1),
                    "validity_years": cert.get("validity_years", 0),
                    "cost": self._cost(cert),
                    "url": self._cert_url(cert["name"]),
                }
            )

        total_cost = sum(item["cost"]["total"] for item in plan_items)
        total_weeks = round(cumulative_weeks, 1)

        return {
            "career": role.get("role", career_goal),
            "certifications": plan_items,
            "summary": {
                "total_certifications": len(plan_items),
                "total_weeks": total_weeks,
                "total_months": round(total_weeks / 4.3, 1),
                "total_cost": round(total_cost, 2),
                "weekly_study_hours": weekly,
            },
        }

    def _order_by_prerequisites(self, certs: List[dict]) -> List[dict]:
        """Topological sort by prerequisite certification names."""
        name_to_cert = {c["name"]: c for c in certs}
        visited: set = set()
        result: List[dict] = []

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            cert = name_to_cert.get(name)
            if not cert:
                return
            for prereq in cert.get("prerequisites", []):
                if prereq in name_to_cert and prereq not in visited:
                    visit(prereq)
            result.append(cert)

        for cert in certs:
            visit(cert["name"])

        return result

    def _cert_url(self, cert_name: str) -> str:
        urls = {
            "Google Cybersecurity Professional Certificate": "https://www.coursera.org/professional-certificates/google-cybersecurity",
            "CompTIA Security+": "https://www.comptia.org/certifications/security",
            "Blue Team Level 1": "https://securityblue.team/",
            "eJPT": "https://ine.com/certifications/ine-security-certified-endpoint-professional",
            "PNPT": "https://tcm-sec.com/pnpt/",
            "OSCP": "https://www.offsec.com/courses/pen-200/",
            "OSWE": "https://www.offsec.com/courses/web-300/",
            "AWS Security Specialty": "https://aws.amazon.com/certification/certified-security-specialty/",
            "CCSK": "https://cloudsecurityalliance.org/education/ccsk/",
            "Azure Security Engineer": "https://learn.microsoft.com/en-us/credentials/certifications/azure-security-engineer/",
            "CSSLP": "https://www.isc2.org/Certifications/CSSLP",
            "GCFA": "https://www.giac.org/certifications/forensic-analyst-gcfa/",
            "CTIA": "https://www.eccouncil.org/accreditations/ctia-certification/",
            "GCTI": "https://www.giac.org/certifications/cyber-threat-intelligence-gcti/",
            "CISSP": "https://www.isc2.org/Certifications/CISSP",
            "CCSP": "https://www.isc2.org/Certifications/CCSP",
            "Certified Kubernetes Security Specialist": "https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/",
            "GCIH": "https://www.giac.org/certifications/incident-handler-gcih/",
            "CISA": "https://www.isaca.org/credentialing/cisa",
            "CRISC": "https://www.isaca.org/credentialing/crisc",
            "ISO 27001 Lead Implementer": "https://pecb.com/en/education-and-certification-for-individuals/iso-27001-lead-implementer",
            "CEH": "https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/",
            "CompTIA CySA+": "https://www.comptia.org/certifications/cybersecurity-analyst",
        }
        return urls.get(cert_name, "#")


certification_planner_service = CertificationPlannerService()