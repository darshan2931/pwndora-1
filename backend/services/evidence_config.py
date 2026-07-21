from enum import Enum
from typing import Dict


class EvidenceSource(str, Enum):
    RESUME_CLAIM = "resume_claim"
    RESUME_EXPERIENCE = "resume_experience"
    GITHUB_LANGUAGE = "github_language"
    GITHUB_TOPIC = "github_topic"
    GITHUB_DEPENDENCY = "github_dependency"
    GITHUB_README = "github_readme"
    GITHUB_AI_ANALYSIS = "github_ai_analysis"
    ASSESSMENT_MATCHED = "assessment_matched"
    ASSESSMENT_COMPLETED = "assessment_completed"
    PROJECT_COMPLETED = "project_completed"
    CERTIFICATION_EARNED = "certification_earned"


SOURCE_WEIGHTS: Dict[EvidenceSource, float] = {
    EvidenceSource.RESUME_CLAIM: 0.15,
    EvidenceSource.RESUME_EXPERIENCE: 0.25,
    EvidenceSource.GITHUB_LANGUAGE: 0.20,
    EvidenceSource.GITHUB_TOPIC: 0.12,
    EvidenceSource.GITHUB_DEPENDENCY: 0.10,
    EvidenceSource.GITHUB_README: 0.08,
    EvidenceSource.GITHUB_AI_ANALYSIS: 0.18,
    EvidenceSource.ASSESSMENT_MATCHED: 0.22,
    EvidenceSource.ASSESSMENT_COMPLETED: 0.30,
    EvidenceSource.PROJECT_COMPLETED: 0.28,
    EvidenceSource.CERTIFICATION_EARNED: 0.35,
}

SOURCE_MAX_CONFIDENCE: Dict[EvidenceSource, float] = {
    EvidenceSource.RESUME_CLAIM: 0.40,
    EvidenceSource.RESUME_EXPERIENCE: 0.60,
    EvidenceSource.GITHUB_LANGUAGE: 0.50,
    EvidenceSource.GITHUB_TOPIC: 0.35,
    EvidenceSource.GITHUB_DEPENDENCY: 0.30,
    EvidenceSource.GITHUB_README: 0.25,
    EvidenceSource.GITHUB_AI_ANALYSIS: 0.45,
    EvidenceSource.ASSESSMENT_MATCHED: 0.55,
    EvidenceSource.ASSESSMENT_COMPLETED: 0.70,
    EvidenceSource.PROJECT_COMPLETED: 0.65,
    EvidenceSource.CERTIFICATION_EARNED: 0.80,
}

MAX_CONFIDENCE_CAP = 0.95
DIMINISHING_RETURN_FACTOR = 0.65


def get_source_weight(source: EvidenceSource) -> float:
    return SOURCE_WEIGHTS.get(source, 0.10)


def get_source_max_confidence(source: EvidenceSource) -> float:
    return SOURCE_MAX_CONFIDENCE.get(source, 0.30)
