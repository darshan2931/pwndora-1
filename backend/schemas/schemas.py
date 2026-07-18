from typing import List, Optional

from pydantic import BaseModel


class CareerAnalysisRequest(BaseModel):
    career_goal: str
    study_hours: int = 10
    manual_skills: Optional[List[str]] = None


class MentorChatRequest(BaseModel):
    assessment_id: str
    question: str


class ResumeUploadRequest(BaseModel):
    career_goal: str
    study_hours: int = 10


class SkillInfo(BaseModel):
    name: str
    category: str = ""
    difficulty: str = ""


class RoadmapStepInfo(BaseModel):
    step: int
    skill: str
    prerequisites: List[str] = []
    estimated_hours: int = 0
    resources: List[str] = []
    project: Optional[str] = None


class ProjectInfo(BaseModel):
    title: str
    difficulty: str
    skills: List[str] = []
    estimated_hours: int = 0


class AssessmentData(BaseModel):
    profile_skills: List[SkillInfo] = []
    career_goal: str
    career_readiness: int = 0
    matched_skills: List[SkillInfo] = []
    missing_skills: List[SkillInfo] = []
    roadmap: List[RoadmapStepInfo] = []
    projects: List[ProjectInfo] = []
    ai_summary: str = ""


class MentorResponse(BaseModel):
    response: str


class StandardResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: List[str] = []


class CareerInfo(BaseModel):
    id: str
    title: str
    description: str


class ProjectRecommendation(BaseModel):
    title: str
    difficulty: str
    skills: List[str]
    estimated_hours: int

