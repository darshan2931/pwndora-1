from typing import List, Optional

from pydantic import BaseModel, field_validator


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


class UserSignUp(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Name must be at most 100 characters")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must be at most 128 characters")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True

