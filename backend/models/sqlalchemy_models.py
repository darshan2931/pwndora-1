from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    career_goal = Column(String(100), nullable=False)
    readiness_score = Column(Integer, default=0)
    matched_skills = Column(JSONB, default=list)
    missing_skills = Column(JSONB, default=list)
    weekly_hours = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    steps = Column(JSONB, default=list)
    total_hours = Column(Integer, default=0)
    estimated_weeks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
