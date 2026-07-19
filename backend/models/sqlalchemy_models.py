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
