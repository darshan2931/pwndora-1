import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# pyrefly: ignore [missing-import]
from ai.service import AIClient, AIService
# pyrefly: ignore [missing-import]
from ai.gemini_client import GeminiClient
# pyrefly: ignore [missing-import]
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
    from models.sqlalchemy_models import Assessment, Roadmap, ChatHistory, KnowledgeCache  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")

    # Initialize Mistral client for assessment/career (resume, roadmap, career explanation)
    mistral_client = None
    mistral_keys_str = os.getenv("MISTRAL_API_KEYS", "") or os.getenv("MISTRAL_API_KEY", "")
    mistral_keys = [k.strip() for k in mistral_keys_str.split(",") if k.strip()]
    if mistral_keys:
        mistral_client = AIClient(api_keys=mistral_keys)
        logger.info("Mistral client initialized (%d key(s))", len(mistral_keys))
    else:
        logger.warning("No MISTRAL_API_KEY found. Assessment features will be limited.")

    # Initialize Gemini client for AI mentor chat
    gemini_client = None
    gemini_keys_str = os.getenv("GEMINI_API_KEY", "")
    gemini_keys = [k.strip() for k in gemini_keys_str.split(",") if k.strip()]
    if gemini_keys:
        gemini_client = GeminiClient(api_keys=gemini_keys)
        logger.info("Gemini client initialized (%d key(s))", len(gemini_keys))
    else:
        logger.warning("No GEMINI_API_KEY found. AI mentor will be unavailable.")

    if mistral_client or gemini_client:
        _ai_service = AIService(mistral_client=mistral_client, gemini_client=gemini_client)
    else:
        logger.warning("No AI API keys found. AI features will be unavailable.")
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
    "https://cyberpath.vercel.app",
    "https://cyberpath-ai.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
