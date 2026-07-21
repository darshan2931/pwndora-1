from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator


class GitHubUserProfile(BaseModel):
    username: Optional[str] = None
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None
    public_repositories: int = 0
    followers: int = 0
    following: int = 0
    account_created_at: Optional[str] = None


class RepositoryMetadata(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    html_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    stars: int = 0
    forks: int = 0
    is_fork: bool = False
    is_archived: bool = False
    topics: List[str] = []
    languages: Dict[str, int] = {}
    default_branch: str = "main"
    size: int = 0
    has_readme: bool = False
    selection_reasons: List[str] = []

    @field_validator("topics", "languages", "selection_reasons", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        return v


class ReadmeData(BaseModel):
    readme_available: bool = False
    readme_text: Optional[str] = None
    readme_character_count: int = 0


class TechEvidenceItem(BaseModel):
    technology: str
    source: str = "github"
    evidence_type: str
    repository: Optional[str] = None
    details: Dict[str, Any] = {}


class CybersecurityRelevance(BaseModel):
    is_relevant: bool = False
    areas: List[str] = []
    evidence: Optional[str] = None


class DemonstratedTechnology(BaseModel):
    name: str
    evidence: str


class RepoAIAnalysis(BaseModel):
    project_purpose: Optional[str] = None
    technical_domains: List[str] = []
    demonstrated_technologies: List[DemonstratedTechnology] = []
    cybersecurity_relevance: CybersecurityRelevance = CybersecurityRelevance()
    complexity: Optional[str] = None
    observable_evidence: List[str] = []

    @field_validator("technical_domains", "observable_evidence", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        return v


class RepositoryEvidence(BaseModel):
    repository: RepositoryMetadata
    readme: ReadmeData = ReadmeData()
    tech_evidence: List[TechEvidenceItem] = []
    ai_analysis: Optional[RepoAIAnalysis] = None

    @field_validator("tech_evidence", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        return v


class GitHubAnalysisResult(BaseModel):
    status: str
    github_profile: Optional[GitHubUserProfile] = None
    repositories_analyzed: int = 0
    repositories: List[RepositoryEvidence] = []
    all_technologies: List[TechEvidenceItem] = []
    message: Optional[str] = None

    @field_validator("repositories", "all_technologies", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        return v


class GitHubProfileResponse(BaseModel):
    username: Optional[str] = None
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None
    public_repositories: int = 0
    followers: int = 0
    following: int = 0
    account_created_at: Optional[str] = None
    fetched_at: Optional[str] = None
    repositories_analyzed: int = 0
    repositories: List[RepositoryMetadata] = []
    processing_status: str = "pending"
    processing_error: Optional[str] = None
    created_at: Optional[str] = None

    @field_validator("repositories", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        return v


class GitHubEvidenceResponse(BaseModel):
    evidence: List[TechEvidenceItem] = []
    repositories_analyzed: int = 0

    @field_validator("evidence", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        return v
