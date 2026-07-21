from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator


class EvidenceSourceDetail(BaseModel):
    source: str
    raw_confidence: float = 0.0
    effective_confidence: float = 0.0
    weight: float = 0.0
    contribution: float = 0.0
    repository: Optional[str] = None
    evidence_text: Optional[str] = None
    details: Dict[str, Any] = {}


class SkillEvidenceItem(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    confidence: float
    confidence_level: str
    sources: List[EvidenceSourceDetail] = []
    evidence_count: int = 0
    strongest_source: Optional[str] = None
    last_updated: Optional[str] = None

    @field_validator("sources", mode="before")
    @classmethod
    def ensure_sources(cls, v):
        if v is None:
            return []
        return v


class SkillEvidenceSummary(BaseModel):
    total_skills: int = 0
    high_confidence: int = 0
    medium_confidence: int = 0
    low_confidence: int = 0
    minimal_confidence: int = 0
    skills: List[SkillEvidenceItem] = []

    @field_validator("skills", mode="before")
    @classmethod
    def ensure_skills(cls, v):
        if v is None:
            return []
        return v


class SkillEvidenceDetail(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    confidence: float
    confidence_level: str
    evidence_count: int
    sources: List[EvidenceSourceDetail] = []
    strongest_source: Optional[str] = None
    last_updated: Optional[str] = None

    @field_validator("sources", mode="before")
    @classmethod
    def ensure_sources(cls, v):
        if v is None:
            return []
        return v


class SkillEvidenceAnalysisResponse(BaseModel):
    status: str
    user_id: Optional[str] = None
    summary: Optional[SkillEvidenceSummary] = None
    message: Optional[str] = None
    cached: bool = False
