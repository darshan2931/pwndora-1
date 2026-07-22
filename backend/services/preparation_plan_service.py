import logging
from typing import Dict, List, Optional

from models.sqlalchemy_models import SkillEvidence
from repositories.opportunity_repositories import (
    CareerOpportunityRepository,
    OpportunityRequirementRepository,
)
from services.opportunity_matching_service import OpportunityMatchingService
from knowledge.loader import knowledge_loader

logger = logging.getLogger(__name__)


class PreparationPlanService:
    """
    Generates personalized preparation plans for job opportunities
    based on match analysis and available learning resources.
    """

    HOURS_PER_SKILL = {
        "critical": 30,
        "high": 25,
        "important": 20,
        "medium": 15,
        "low": 10,
        "beneficial": 10,
    }

    def __init__(self):
        self.opp_repo = CareerOpportunityRepository()
        self.req_repo = OpportunityRequirementRepository()
        self.matcher = OpportunityMatchingService()

    def generate_plan(
        self,
        user_id: str,
        opportunity_id: str,
        user_evidence: List[SkillEvidence],
        user_certifications: List[str],
    ) -> Dict:
        match_result = self.matcher.calculate_match(
            user_id=user_id,
            opportunity_id=opportunity_id,
            user_evidence=user_evidence,
            user_certifications=user_certifications,
        )

        if "error" in match_result:
            return {"error": match_result["error"]}

        opp = self.opp_repo.get_by_id(opportunity_id)
        if not opp:
            return {"error": "Opportunity not found"}

        requirements = self.req_repo.get_by_opportunity_id(opportunity_id)

        evidence_map = self._build_evidence_map(user_evidence)

        steps = self._build_preparation_steps(
            match_result["missing_skills"],
            requirements,
            evidence_map,
        )

        total_hours = sum(s["estimated_hours"] for s in steps)

        plan = {
            "opportunity_id": opportunity_id,
            "opportunity_title": opp.title,
            "organization": opp.organization,
            "overall_score": match_result["overall_score"],
            "category": match_result["category"],
            "missing_skills": match_result["missing_skills"],
            "strengths": match_result["strengths"],
            "recommendation": match_result["recommendation"],
            "preparation_steps": steps,
            "total_estimated_hours": total_hours,
            "estimated_weeks": max(1, round(total_hours / 10)),
            "priority_order": [s["skill"] for s in steps],
        }

        return plan

    def _build_preparation_steps(
        self,
        missing_skills: List[Dict],
        requirements: List,
        evidence_map: Dict,
    ) -> List[Dict]:
        steps = []
        skills_data = knowledge_loader.get_skills()

        for skill_info in missing_skills[:5]:
            skill_name = skill_info["skill"]
            importance = skill_info["importance"]

            learning_resources = self._find_learning_resources(skill_name, skills_data)
            practice = self._suggest_practice(skill_name)
            current_level = self._assess_current_level(skill_name, evidence_map)
            estimated_hours = self.HOURS_PER_SKILL.get(importance, 20)

            steps.append({
                "skill": skill_name,
                "importance": importance,
                "importance_score": skill_info.get("importance_score", 50),
                "current_level": current_level,
                "target_level": "intermediate",
                "estimated_hours": estimated_hours,
                "learning_resources": learning_resources,
                "practice_activities": practice,
                "prerequisites": self._get_prerequisites(skill_name, skills_data),
            })

        return steps

    def _find_learning_resources(self, skill_name: str, skills_data: List) -> List[Dict]:
        resources = []
        for skill in skills_data:
            if skill.get("name", "").lower() == skill_name.lower():
                for lr in skill.get("learning_resources", []):
                    resources.append({
                        "title": lr.get("title", ""),
                        "type": lr.get("type", "course"),
                        "url": lr.get("url", "#"),
                        "free": lr.get("free", True),
                    })
                break
        return resources[:3]

    def _suggest_practice(self, skill_name: str) -> List[str]:
        suggestions = {
            "SIEM": ["Set up a home Splunk lab", "Analyze sample logs on TryHackMe"],
            "Linux Fundamentals": ["Complete OverTheWire Bandit", "Practice command line daily"],
            "Networking Fundamentals": ["Build a home network lab", "Complete Cisco Packet Tracer labs"],
            "Scripting": ["Automate a daily task with Python", "Build a security tool"],
            "Incident Response": ["Practice with DFIR training scenarios", "Volunteer for CTF IR challenges"],
            "Threat Hunting": ["Hunt in sample PCAPs", "Practice with MITRE ATT&CK mappings"],
            "Cloud Security": ["Set up AWS free tier security controls", "Practice IAM policies"],
            "Web Application Security": ["Complete PortSwigger Web Security Academy", "Practice on HackTheBox web challenges"],
            "Malware Analysis": ["Analyze samples in any.run", "Practice reverse engineering basics"],
            "Vulnerability Assessment": ["Run Nessus on a home lab", "Practice with OpenVAS"],
            "Digital Forensics": ["Practice with DFIR training images", "Complete Autopsy tutorials"],
            "Cryptography": ["Implement basic encryption algorithms", "Complete crypto CTF challenges"],
            "Network Security": ["Configure firewall rules", "Set up IDS/IPS at home"],
            "Identity and Access Management": ["Set up LDAP/AD lab", "Practice RBAC configurations"],
            "Risk Management": ["Practice risk assessment frameworks", "Study NIST RMF"],
            "Compliance": ["Study SOC 2 requirements", "Practice audit checklists"],
            "Security Frameworks": ["Map controls to MITRE ATT&CK", "Study NIST CSF"],
            "Reverse Engineering": ["Practice on CrackMe challenges", "Use Ghidra tutorials"],
            "Log Analysis": ["Analyze real-world log samples", "Build detection rules"],
            "AWS Security": ["Complete AWS Security Specialty labs", "Practice GuardDuty"],
            "Threat Modeling": ["Practice STRIDE on sample apps", "Study Microsoft Threat Modeling Tool"],
        }
        return suggestions.get(skill_name, ["Complete related online labs", "Build a personal project"])

    def _assess_current_level(self, skill_name: str, evidence_map: Dict) -> str:
        skill_evidence = evidence_map.get(skill_name.lower(), [])
        if not skill_evidence:
            return "not_started"
        max_conf = max(e.confidence for e in skill_evidence)
        if max_conf >= 70:
            return "intermediate"
        if max_conf >= 40:
            return "beginner"
        return "not_started"

    def _get_prerequisites(self, skill_name: str, skills_data: List) -> List[str]:
        for skill in skills_data:
            if skill.get("name", "").lower() == skill_name.lower():
                return skill.get("prerequisites", [])
        return []

    def _build_evidence_map(self, evidence: List[SkillEvidence]) -> Dict[str, List[SkillEvidence]]:
        evidence_map: Dict[str, List[SkillEvidence]] = {}
        for ev in evidence:
            skill_name = ev.skill_name.lower().strip()
            if skill_name not in evidence_map:
                evidence_map[skill_name] = []
            evidence_map[skill_name].append(ev)
        return evidence_map
