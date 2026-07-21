from enum import Enum
from typing import Dict, Optional


class SkillImportance(Enum):
    REQUIRED = 0.9
    CRITICAL = 0.7
    IMPORTANT = 0.5
    BENEFICIAL = 0.3


class MinimumConfidence(Enum):
    REQUIRED = 0.80
    CRITICAL = 0.65
    IMPORTANT = 0.50
    BENEFICIAL = 0.30


class GapStatus(Enum):
    COVERED = "covered"
    MINIMAL = "minimal"
    PARTIAL = "partial"
    CRITICAL = "critical"
    MISSING = "missing"


class PriorityLevel(Enum):
    HIGHEST = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


ROLE_SKILL_CONFIGS: Dict[str, Dict[str, Dict[str, str]]] = {
    "SOC Analyst": {
        "required_skills": {
            "Networking": "critical",
            "Linux": "important",
            "Windows": "important",
            "SIEM": "required",
            "Log Analysis": "required",
            "Incident Response": "required",
            "MITRE ATT&CK": "critical",
        },
        "optional_skills": {
            "Python": "beneficial",
            "Bash": "beneficial",
            "PowerShell": "beneficial",
            "EDR": "beneficial",
        },
    },
    "Penetration Tester": {
        "required_skills": {
            "Linux": "critical",
            "Networking": "critical",
            "Python": "important",
            "Bash": "important",
            "Nmap": "required",
            "Burp Suite": "required",
            "OWASP Top 10": "required",
            "Active Directory": "important",
        },
        "optional_skills": {
            "Metasploit": "beneficial",
            "Privilege Escalation": "beneficial",
            "Enumeration": "beneficial",
        },
    },
    "Cloud Security Engineer": {
        "required_skills": {
            "Linux": "critical",
            "AWS": "required",
            "IAM": "required",
            "Docker": "required",
            "Kubernetes": "important",
            "Terraform": "important",
        },
        "optional_skills": {
            "Azure": "beneficial",
            "GCP": "beneficial",
            "CI/CD": "beneficial",
        },
    },
    "Application Security Engineer": {
        "required_skills": {
            "Secure Coding": "required",
            "OWASP Top 10": "required",
            "SAST": "required",
            "DAST": "required",
            "CI/CD": "important",
            "Docker": "important",
            "Threat Modeling": "critical",
        },
        "optional_skills": {
            "Python": "beneficial",
            "JavaScript": "beneficial",
            "Kubernetes": "beneficial",
        },
    },
    "Digital Forensics Analyst": {
        "required_skills": {
            "Windows": "critical",
            "Linux": "critical",
            "Memory Analysis": "required",
            "Disk Analysis": "required",
            "Timeline Analysis": "required",
        },
        "optional_skills": {
            "Python": "beneficial",
            "Malware Analysis": "beneficial",
            "Network Forensics": "beneficial",
        },
    },
    "Threat Intelligence Analyst": {
        "required_skills": {
            "MITRE ATT&CK": "required",
            "OSINT": "required",
            "Log Analysis": "important",
            "SIEM": "critical",
            "Python": "important",
        },
        "optional_skills": {
            "Malware Analysis": "beneficial",
            "Dark Web Research": "beneficial",
            "YARA": "beneficial",
        },
    },
    "Security Architect": {
        "required_skills": {
            "Networking": "critical",
            "Firewalls": "critical",
            "IAM": "required",
            "AWS": "critical",
            "Docker": "important",
            "Kubernetes": "important",
            "Threat Modeling": "critical",
            "Secure Coding": "required",
        },
        "optional_skills": {
            "Terraform": "beneficial",
            "CI/CD": "beneficial",
            "Compliance Frameworks": "beneficial",
        },
    },
    "DevSecOps Engineer": {
        "required_skills": {
            "CI/CD": "required",
            "Docker": "required",
            "Kubernetes": "important",
            "SAST": "required",
            "DAST": "required",
            "Linux": "critical",
            "Python": "important",
            "Terraform": "important",
        },
        "optional_skills": {
            "AWS": "beneficial",
            "GCP": "beneficial",
            "Container Security": "beneficial",
            "Secrets Management": "beneficial",
        },
    },
    "GRC Analyst": {
        "required_skills": {
            "Compliance Frameworks": "required",
            "Risk Assessment": "required",
            "Security Auditing": "required",
            "NIST": "critical",
            "ISO 27001": "critical",
        },
        "optional_skills": {
            "SOC 2": "beneficial",
            "Business Continuity": "beneficial",
            "Incident Response": "beneficial",
        },
    },
    "Incident Responder": {
        "required_skills": {
            "Incident Response": "required",
            "Log Analysis": "critical",
            "SIEM": "critical",
            "Memory Analysis": "required",
            "Network Forensics": "required",
            "Linux": "important",
            "Windows": "important",
        },
        "optional_skills": {
            "Malware Analysis": "beneficial",
            "OSINT": "beneficial",
            "YARA": "beneficial",
        },
    },
}


def get_importance_level(role_id: str, skill_id: str, is_required: bool) -> SkillImportance:
    role_config = ROLE_SKILL_CONFIGS.get(role_id, {})
    key = "required_skills" if is_required else "optional_skills"
    skill_config = role_config.get(key, {}).get(skill_id)

    mapping = {
        "required": SkillImportance.REQUIRED,
        "critical": SkillImportance.CRITICAL,
        "important": SkillImportance.IMPORTANT,
        "beneficial": SkillImportance.BENEFICIAL,
    }
    return mapping.get(skill_config, SkillImportance.IMPORTANT)


def get_minimum_confidence(role_id: str, skill_id: str, is_required: bool) -> float:
    importance = get_importance_level(role_id, skill_id, is_required)
    mapping = {
        SkillImportance.REQUIRED: MinimumConfidence.REQUIRED.value,
        SkillImportance.CRITICAL: MinimumConfidence.CRITICAL.value,
        SkillImportance.IMPORTANT: MinimumConfidence.IMPORTANT.value,
        SkillImportance.BENEFICIAL: MinimumConfidence.BENEFICIAL.value,
    }
    return mapping[importance]


def get_importance_score(role_id: str, skill_id: str, is_required: bool) -> float:
    importance = get_importance_level(role_id, skill_id, is_required)
    return importance.value
