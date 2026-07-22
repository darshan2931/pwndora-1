import logging
from enum import Enum
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class MentorMode(str, Enum):
    CAREER_ANALYSIS = "career_analysis"
    ROADMAP_GUIDANCE = "roadmap_guidance"
    PROJECT_MENTOR = "project_mentor"
    SKILL_MENTOR = "skill_mentor"
    PROGRESS_REVIEW = "progress_review"
    INTERVIEW_PREPARATION = "interview_preparation"
    GENERAL = "general"


MODE_CONTEXT_REQUIREMENTS: Dict[MentorMode, Set[str]] = {
    MentorMode.CAREER_ANALYSIS: {"user", "readiness", "strengths", "weak_skills", "priority_gaps", "next_best_skill", "evidence_summary"},
    MentorMode.ROADMAP_GUIDANCE: {"user", "roadmap", "readiness", "strengths", "developing"},
    MentorMode.PROJECT_MENTOR: {"user", "roadmap", "evidence_summary"},
    MentorMode.SKILL_MENTOR: {"user", "readiness", "strengths", "developing", "weak_skills"},
    MentorMode.PROGRESS_REVIEW: {"user", "recent_changes", "readiness", "evidence_summary"},
    MentorMode.INTERVIEW_PREPARATION: {"user", "strengths", "developing", "weak_skills", "evidence_summary", "github"},
    MentorMode.GENERAL: set(),  # empty = all fields
}


def detect_mode(question: str) -> MentorMode:
    q = question.lower()
    
    interview_kw = ["interview", "hiring", "job", "resume tip", "portfolio", "cover letter", "salary", "recruiter"]
    if any(kw in q for kw in interview_kw):
        return MentorMode.INTERVIEW_PREPARATION
    
    skill_kw = ["teach me", "explain", "what is", "how does", "learn", "tutorial", "guide me through"]
    skill_names = ["siem", "python", "linux", "nmap", "burp", "wireshark", "firewall", "incident response", 
                   "log analysis", "networking", "aws", "docker", "kubernetes", "mitre"]
    if any(kw in q for kw in skill_kw) or any(s in q for s in skill_names):
        return MentorMode.SKILL_MENTOR
    
    project_kw = ["project", "build", "implement", "architecture", "design", "code", "develop", "milestone"]
    if any(kw in q for kw in project_kw):
        return MentorMode.PROJECT_MENTOR
    
    roadmap_kw = ["roadmap", "order", "sequence", "why this", "next step", "phase", "prerequisite"]
    if any(kw in q for kw in roadmap_kw):
        return MentorMode.ROADMAP_GUIDANCE
    
    progress_kw = ["progress", "improve", "changed", "readiness increase", "what did i", "recent", "update"]
    if any(kw in q for kw in progress_kw):
        return MentorMode.PROGRESS_REVIEW
    
    career_kw = ["career", "path", "next skill", "what should i", "recommend", "gap", "blocked", "readiness"]
    if any(kw in q for kw in career_kw):
        return MentorMode.CAREER_ANALYSIS
    
    return MentorMode.GENERAL


def get_context_keys(mode: MentorMode) -> Set[str]:
    return MODE_CONTEXT_REQUIREMENTS.get(mode, set())


def get_mode_description(mode: MentorMode) -> str:
    descriptions = {
        MentorMode.CAREER_ANALYSIS: "Explain current career position, strengths, weaknesses, readiness, blockers, and next action.",
        MentorMode.ROADMAP_GUIDANCE: "Explain the current roadmap step, why it matters, prerequisites, and what completion means.",
        MentorMode.PROJECT_MENTOR: "Help with project planning, architecture, milestones, implementation strategy, and portfolio presentation.",
        MentorMode.SKILL_MENTOR: "Teach about a specific skill - why it matters, current confidence, prerequisites, and practical learning approach.",
        MentorMode.PROGRESS_REVIEW: "Review recent progress, explain what improved, evidence changes, readiness movement, and what should happen next.",
        MentorMode.INTERVIEW_PREPARATION: "Generate role-specific interview preparation based on verified skills, projects, and target role.",
        MentorMode.GENERAL: "General cybersecurity career guidance and mentorship.",
    }
    return descriptions.get(mode, "General career guidance.")
