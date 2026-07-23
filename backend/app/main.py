import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.logging_config import setup_logging

setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))

from app.ai.ai_service import AIService  # noqa: E402
from core.middleware import AccessLogMiddleware  # noqa: E402
from utils.middleware.rate_limiter import RateLimitMiddleware  # noqa: E402

load_dotenv()

logger = logging.getLogger(__name__)

_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    if _ai_service is None:
        raise RuntimeError("AI service not initialized. Check API keys.")
    return _ai_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _ai_service

    from database.session import engine, Base
    from models.sqlalchemy_models import (  # noqa: F401
        User, CyberProfile, Assessment, Roadmap, ChatMemory, ChatHistory,
        ResumeAnalysis, ResumeReview, Skill, Project, ResumeProfile,
        GitHubProfile, GitHubRepositoryEvidence, SkillEvidence,
        UserSkillProfile, CareerRoleAnalysis, MentorMemory,
        CareerOpportunity, OpportunityRequirement, OpportunityMatch,
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")

    from sqlalchemy import text as sa_text
    from database.session import engine as db_engine
    is_pg = str(db_engine.url).startswith("postgresql")
    if is_pg:
        _migrations = [
            ("roadmaps", "user_id", "UUID"),
            ("roadmaps", "version", "INTEGER DEFAULT 1"),
            ("roadmaps", "generation_reason", "VARCHAR(100)"),
            ("roadmaps", "readiness_score_at_creation", "INTEGER DEFAULT 0"),
            ("roadmaps", "phases", "JSONB DEFAULT '[]'::jsonb"),
            ("assessments", "learning_preferences", "JSONB DEFAULT '[]'::jsonb"),
            ("cyber_profiles", "name", "VARCHAR(255) DEFAULT ''"),
            ("cyber_profiles", "email", "VARCHAR(255) DEFAULT ''"),
            ("cyber_profiles", "experience", "VARCHAR(50) DEFAULT 'beginner'"),
            ("cyber_profiles", "target_role", "VARCHAR(100) DEFAULT ''"),
            ("cyber_profiles", "target_role_category", "VARCHAR(100) DEFAULT ''"),
            ("cyber_profiles", "avatar_initials", "VARCHAR(10) DEFAULT ''"),
            ("cyber_profiles", "current_streak", "INTEGER DEFAULT 0"),
            ("cyber_profiles", "total_study_hours", "INTEGER DEFAULT 0"),
            ("cyber_profiles", "learning_preferences", "JSONB DEFAULT '[]'::jsonb"),
        ]
        with db_engine.begin() as conn:
            for table, col, col_type in _migrations:
                try:
                    conn.execute(sa_text(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type}'))
                except Exception:
                    pass
        logger.info("Database schema migrations applied.")

    from repositories.opportunity_repositories import CareerOpportunityRepository
    import json
    opp_repo = CareerOpportunityRepository()
    seed_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "opportunities.json")
    if os.path.exists(seed_path):
        with open(seed_path) as f:
            opportunities = json.load(f)
        seeded = opp_repo.seed_opportunities(opportunities)
        if seeded > 0:
            logger.info("Seeded %d career opportunities.", seeded)

    _ai_service = AIService(provider_name="gemini")

    if _ai_service.is_configured():
        logger.info("AI Intelligence Layer initialized successfully.")
    else:
        logger.warning("No AI API keys found. Running in MOCK mode.")

    yield
    _ai_service = None


app = FastAPI(
    title="CyberPath AI",
    description="AI-powered Cybersecurity Career Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

_cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst=10)

from app.api.routes import router  # noqa: E402

app.include_router(router, prefix="/api/v1")


def _format_error_response(detail):
    if isinstance(detail, dict):
        message = detail.get("message", str(detail))
        code = detail.get("code", "HTTP_ERROR")
    else:
        message = str(detail)
        code = "HTTP_ERROR"
    return {"success": False, "error": {"code": code, "message": message}}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content=_format_error_response(exc.detail))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
            },
        },
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
