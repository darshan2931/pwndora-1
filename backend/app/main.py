import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# pyrefly: ignore [missing-import]
from app.ai.ai_service import AIService
from core.middleware import AccessLogMiddleware
# pyrefly: ignore [missing-import]
from utils.middleware.rate_limiter import RateLimitMiddleware

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

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
    from models.sqlalchemy_models import User, CyberProfile, Assessment, Roadmap, ChatMemory, ChatHistory, ResumeAnalysis, ResumeReview, Skill, Project  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")

    # Initialize new AI Intelligence Layer
    # Defaults to 'gemini' provider, falls back to 'mistral'
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

# pyrefly: ignore [missing-import]
from app.api.routes import router

app.include_router(router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    from fastapi.exceptions import HTTPException as FastAPIHTTPException
    if isinstance(exc, FastAPIHTTPException):
        raise exc
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"},
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
