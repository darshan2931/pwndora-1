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
        raise RuntimeError("AI service not initialized. Check MISTRAL_API_KEY.")
    return _ai_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _ai_service

    from database.session import engine, Base
    from models.sqlalchemy_models import Assessment, Roadmap, ChatHistory, KnowledgeCache  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        api_keys = [k.strip() for k in gemini_key.split(",") if k.strip()]
        from ai.gemini_client import GeminiClient
        client = GeminiClient(api_keys=api_keys)
        _ai_service = AIService(client=client)
        logger.info("AI service initialized with Gemini API (%d key(s))", len(api_keys))
    else:
        keys_str = os.getenv("MISTRAL_API_KEYS", "")
        if not keys_str:
            keys_str = os.getenv("MISTRAL_API_KEY", "")

        api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if api_keys:
            client = AIClient(api_keys=api_keys)
            _ai_service = AIService(client=client)
            logger.info("AI service initialized with Mistral API (%d key(s))", len(api_keys))
        else:
            logger.warning("No AI API keys found. AI features will use demo data.")
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
