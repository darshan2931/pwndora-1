import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
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


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    from fastapi.exceptions import HTTPException as FastAPIHTTPException
    if isinstance(exc, FastAPIHTTPException):
        detail = exc.detail if hasattr(exc, "detail") else str(exc)
        if isinstance(detail, dict):
            message = detail.get("message", str(detail))
            code = detail.get("code", "HTTP_ERROR")
        else:
            message = str(detail)
            code = "HTTP_ERROR"
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": code,
                    "message": message,
                },
            },
        )
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
