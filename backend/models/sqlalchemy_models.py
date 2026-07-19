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


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (Index("ix_assessments_user_id", "user_id"),)

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False)
    career_goal = Column(String(100), nullable=False)
    readiness_score = Column(Integer, default=0)
    matched_skills = Column(PortableJSON(), default=list)
    missing_skills = Column(PortableJSON(), default=list)
    weekly_hours = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(PortableUUID(), unique=True, nullable=False)
    steps = Column(PortableJSON(), default=list)
    total_hours = Column(Integer, default=0)
    estimated_weeks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), nullable=False, index=True)
    assessment_id = Column(PortableUUID(), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeCache(Base):
    __tablename__ = "knowledge_cache"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    data = Column(PortableJSON(), nullable=False)
    prompt_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
