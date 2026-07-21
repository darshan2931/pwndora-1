from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GapStatus(str, Enum):
    COVERED = "covered"
    MINIMAL = "minimal"
    PARTIAL = "partial"
    CRITICAL = "critical"
    MISSING = "missing"


class SkillImportance(str, Enum):
    REQUIRED = "required"
    CRITICAL = "critical"
    IMPORTANT = "important"
    BENEFICIAL = "beneficial"


class PriorityLevel(str, Enum):
    HIGHEST = "highest"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SkillGap(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    confidence: float = Field(ge=0, le=1)
    minimum_confidence: float = Field(ge=0, le=1)
    gap_size: float = Field(ge=0, le=1)
    gap_status: GapStatus
    importance: SkillImportance
    importance_score: float = Field(ge=0, le=1)
    is_required: bool
    has_prerequisites: bool
    blocked_by: List[str] = Field(default_factory=list)
    unblocked_skills: List[str] = Field(default_factory=list)
    priority_score: float = Field(ge=0, le=1)
    priority_level: PriorityLevel
    evidence_sources: List[Dict[str, Any]] = Field(default_factory=list)
    recommendation_reason: str


class NextSkillRecommendation(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    confidence: float
    gap_size: float
    importance: SkillImportance
    priority_score: float
    estimated_hours: Optional[int] = None
    prerequisites_met: bool
    blockers: List[str] = Field(default_factory=list)
    recommendation_reason: str
    learning_resources: List[Dict[str, Any]] = Field(default_factory=list)


class ReadinessBreakdown(BaseModel):
    required_skills: Dict[str, Any]
    optional_skills: Dict[str, Any]
    overall_readiness: float
    skill_gaps: List[SkillGap]


class PriorityCategory(BaseModel):
    highest: List[SkillGap] = Field(default_factory=list)
    high: List[SkillGap] = Field(default_factory=list)
    medium: List[SkillGap] = Field(default_factory=list)
    low: List[SkillGap] = Field(default_factory=list)


class RoleGapAnalysisResult(BaseModel):
    role_id: str
    role_name: str
    role_description: str
    readiness_score: float = Field(ge=0, le=1)
    readiness_level: str
    total_skills: int
    covered_count: int
    partial_count: int
    missing_count: int
    skill_gaps: List[SkillGap]
    priority_breakdown: PriorityCategory
    recommended_next_skill: Optional[NextSkillRecommendation] = None
    learning_path: List[Dict[str, Any]] = Field(default_factory=list)
    ai_explanation: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class RoleSelectRequest(BaseModel):
    role_id: str


class RoleSelectResponse(BaseModel):
    role_id: str
    role_name: str
    message: str


class GapAnalysisResponse(BaseModel):
    role_id: str
    role_name: str
    role_description: str
    readiness_score: float
    readiness_level: str
    total_skills: int
    covered_count: int
    partial_count: int
    missing_count: int
    skill_gaps: List[SkillGap]
    priority_breakdown: PriorityCategory
    recommended_next_skill: Optional[NextSkillRecommendation] = None
    learning_path: List[Dict[str, Any]]
    ai_explanation: Optional[str] = None
    analyzed_at: datetime


class RoleListItem(BaseModel):
    role_id: str
    role_name: str
    description: str
    required_skills_count: int
    optional_skills_count: int
    recommended_certifications: List[str]
    estimated_duration: Optional[str] = None


class NextSkillResponse(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    confidence: float
    gap_size: float
    importance: str
    priority_score: float
    estimated_hours: Optional[int] = None
    prerequisites_met: bool
    blockers: List[str]
    recommendation_reason: str
    learning_resources: List[Dict[str, Any]]
