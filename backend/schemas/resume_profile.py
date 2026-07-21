from typing import List, Optional
from pydantic import BaseModel, field_validator


class EducationEntry(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExperienceEntry(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    technologies: List[str] = []


class ExtractedSkill(BaseModel):
    name: str
    category: Optional[str] = None
    source: str = "resume"


class ProjectEntry(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = []
    url: Optional[str] = None


class CertificationEntry(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None


class ExtractedURLs(BaseModel):
    github: List[str] = []
    linkedin: List[str] = []
    portfolio: List[str] = []
    personal_website: List[str] = []
    other: List[str] = []


class ResumeProfileData(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    education: List[EducationEntry] = []
    experience: List[ExperienceEntry] = []
    skills: List[ExtractedSkill] = []
    projects: List[ProjectEntry] = []
    certifications: List[CertificationEntry] = []
    urls: ExtractedURLs = ExtractedURLs()

    @field_validator("education", "experience", "skills", "projects", "certifications", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        return v


class ResumeExtractionMetadata(BaseModel):
    file_type: Optional[str] = None
    character_count: int = 0
    page_count: Optional[int] = None


class ResumeProfileResponse(BaseModel):
    id: str
    status: str
    profile: Optional[ResumeProfileData] = None
    urls: Optional[ExtractedURLs] = None
    metadata: Optional[ResumeExtractionMetadata] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
