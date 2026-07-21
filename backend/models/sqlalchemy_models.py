import json
import uuid

from sqlalchemy import Column, String, Integer, DateTime, Text, func, Index, TypeDecorator, types


from database.session import Base


class PortableUUID(TypeDecorator):
    """UUID type that works on both PostgreSQL and SQLite."""
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(str(value))
        return value


class PortableJSON(TypeDecorator):
    """JSON type that uses JSONB on PostgreSQL and JSON on SQLite."""
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import JSONB
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(types.JSON())

    def process_bind_param(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            if isinstance(value, (dict, list)):
                return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
        return value


class User(Base):
    __tablename__ = "users"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CyberProfile(Base):
    __tablename__ = "cyber_profiles"
    __table_args__ = (Index("ix_cyber_profiles_user_id", "user_id"),)

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False)
    career_goal = Column(String(100), nullable=False)
    readiness_score = Column(Integer, default=0)
    known_skills = Column(PortableJSON(), default=list)
    missing_skills = Column(PortableJSON(), default=list)
    completed_skills = Column(PortableJSON(), default=list)
    projects = Column(PortableJSON(), default=list)
    certifications = Column(PortableJSON(), default=list)
    achievements = Column(PortableJSON(), default=list)
    learning_preference = Column(String(50), default="hands-on")
    weekly_hours = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    career_goal = Column(String(100), nullable=False)
    readiness_score = Column(Integer, default=0)
    matched_skills = Column(PortableJSON(), default=list)
    missing_skills = Column(PortableJSON(), default=list)
    weekly_hours = Column(Integer, default=10)
    learning_preferences = Column(PortableJSON(), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(PortableUUID(), nullable=False, index=True)
    steps = Column(PortableJSON(), default=list)
    total_hours = Column(Integer, default=0)
    estimated_weeks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatMemory(Base):
    __tablename__ = "chat_memory"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    important_facts = Column(PortableJSON(), default=list)
    next_goal = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    file_path = Column(String(255), nullable=False)
    career_goal = Column(String(100), nullable=False)
    extracted_data = Column(PortableJSON(), default=dict)
    feedback = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    assessment_id = Column(PortableUUID(), nullable=True)
    session_id = Column(String(100), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResumeReview(Base):
    __tablename__ = "resume_reviews"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    career_goal = Column(String(100), nullable=False)
    feedback = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(50), default="learning") # learning, completed
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="in-progress")
    github_link = Column(String(255))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")
    reward_points = Column(Integer, default=50)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    study_hours = Column(Integer, default=0)
    quizzes_taken = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"
    
    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    week_start = Column(DateTime(timezone=True), nullable=False)
    summary = Column(Text, nullable=False)
    achievements = Column(PortableJSON(), default=list)
    next_focus = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeCache(Base):
    __tablename__ = "knowledge_cache"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    data = Column(PortableJSON(), nullable=False)
    prompt_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)


class ResumeProfile(Base):
    __tablename__ = "resume_profiles"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(Integer, default=0)
    raw_text = Column(Text, nullable=True)
    extracted_profile = Column(PortableJSON(), default=dict)
    extracted_urls = Column(PortableJSON(), default=dict)
    processing_status = Column(String(20), default="uploaded")
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GitHubProfile(Base):
    __tablename__ = "github_profiles"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    resume_profile_id = Column(PortableUUID(), nullable=True)
    username = Column(String(100), nullable=False)
    profile_url = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    public_repositories = Column(Integer, default=0)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    account_created_at = Column(String(50), nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    processing_status = Column(String(20), default="pending")
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GitHubRepositoryEvidence(Base):
    __tablename__ = "github_repository_evidence"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    github_profile_id = Column(PortableUUID(), nullable=False, index=True)
    repository_name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    repository_url = Column(String(500), nullable=False)
    languages = Column(PortableJSON(), default=dict)
    topics = Column(PortableJSON(), default=list)
    dependencies = Column(PortableJSON(), default=list)
    readme_text = Column(Text, nullable=True)
    readme_available = Column(Integer, default=0)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    is_fork = Column(Integer, default=0)
    is_archived = Column(Integer, default=0)
    created_at_github = Column(String(50), nullable=True)
    updated_at_github = Column(String(50), nullable=True)
    pushed_at_github = Column(String(50), nullable=True)
    selection_reasons = Column(PortableJSON(), default=list)
    ai_analysis = Column(PortableJSON(), default=dict)
    tech_evidence = Column(PortableJSON(), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SkillEvidence(Base):
    __tablename__ = "skill_evidence"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    skill_id = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    confidence = Column(Integer, default=0)
    confidence_level = Column(String(20), default="minimal")
    sources = Column(PortableJSON(), default=list)
    evidence_count = Column(Integer, default=0)
    strongest_source = Column(String(50), nullable=True)
    last_updated = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserSkillProfile(Base):
    __tablename__ = "user_skill_profiles"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    total_skills = Column(Integer, default=0)
    high_confidence_count = Column(Integer, default=0)
    medium_confidence_count = Column(Integer, default=0)
    low_confidence_count = Column(Integer, default=0)
    minimal_confidence_count = Column(Integer, default=0)
    average_confidence = Column(Integer, default=0)
    analysis_status = Column(String(20), default="pending")
    analysis_error = Column(Text, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CareerRoleAnalysis(Base):
    __tablename__ = "career_role_analyses"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    role_id = Column(String(100), nullable=False)
    role_name = Column(String(100), nullable=False)
    readiness_score = Column(Integer, default=0)
    readiness_level = Column(String(20), default="not_started")
    total_skills = Column(Integer, default=0)
    covered_count = Column(Integer, default=0)
    partial_count = Column(Integer, default=0)
    missing_count = Column(Integer, default=0)
    skill_gaps = Column(PortableJSON(), default=list)
    priority_breakdown = Column(PortableJSON(), default=dict)
    recommended_next_skill = Column(PortableJSON(), nullable=True)
    learning_path = Column(PortableJSON(), default=list)
    ai_explanation = Column(Text, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
