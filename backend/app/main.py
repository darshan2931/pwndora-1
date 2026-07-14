import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai.service import AIClient, AIService
from core.middleware import AccessLogMiddleware

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    if _ai_service is None:
        raise RuntimeError("AI service not initialized. Check MISTRAL_API_KEY.")
    return _ai_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _ai_service
    keys_str = os.getenv("MISTRAL_API_KEYS", "")
    if not keys_str:
        keys_str = os.getenv("MISTRAL_API_KEY", "")
    
    api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
    if api_keys:
        client = AIClient(api_keys=api_keys)
        _ai_service = AIService(client=client)
    yield
    _ai_service = None


app = FastAPI(
    title="CyberPath AI",
    description="AI-powered Cybersecurity Career Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AccessLogMiddleware)


from app.api.routes import router

app.include_router(router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "errors": [str(exc)]},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
