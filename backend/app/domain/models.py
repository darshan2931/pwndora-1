from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Skill:
    name: str
    category: str
    difficulty: str  # beginner, intermediate, advanced
    prerequisites: List[str] = field(default_factory=list)
    unlocks: List[str] = field(default_factory=list)
    estimated_hours: int = 10
    related_tools: List[str] = field(default_factory=list)
    learning_resources: List[str] = field(default_factory=list)


@dataclass
class Career:
    id: str
    title: str
    description: str
    required_skills: List[str]
    optional_skills: List[str] = field(default_factory=list)
    recommended_certifications: List[str] = field(default_factory=list)
    suggested_projects: List[str] = field(default_factory=list)


@dataclass
class CyberProfile:
    name: Optional[str] = None
    skills: List[Skill] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    experience_years: int = 0
    education: List[str] = field(default_factory=list)
    projects_completed: List[str] = field(default_factory=list)
    labs_completed: int = 0
    streak_days: int = 0
    achievements: List[str] = field(default_factory=list)


@dataclass
class Assessment:
    cyber_profile: CyberProfile
    target_career: Career
    matched_skills: List[Skill] = field(default_factory=list)
    missing_skills: List[Skill] = field(default_factory=list)
    readiness_score: int = 0


@dataclass
class RoadmapStep:
    step: int
    skill: Skill
    prerequisites: List[str] = field(default_factory=list)
    estimated_hours: int = 10
    resources: List[str] = field(default_factory=list)
    project: Optional[str] = None


@dataclass
class Roadmap:
    steps: List[RoadmapStep] = field(default_factory=list)
    total_hours: int = 0
    estimated_weeks: int = 0


@dataclass
class Project:
    title: str
    difficulty: str
    skills_demonstrated: List[str]
    estimated_time_hours: int
    description: str = ""
    github_deliverables: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    next_skill: Optional[str] = None
    next_project: Optional[str] = None
    next_certification: Optional[str] = None
    reason: str = ""
    estimated_hours: int = 0
    difficulty: str = ""


@dataclass
class ChatSummary:
    session_id: str
    summary_text: str
    important_facts: List[str] = field(default_factory=list)
    next_goal: str = ""
