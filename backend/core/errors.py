"""Standardized error response utilities for CyberPath AI.

All API error responses follow a consistent envelope:
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human-readable description",
        "details": [...]   # optional additional context
    }
}
"""
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse


class ErrorCode:
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    NO_DATA = "NO_DATA"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """Build a standardized error JSON response."""
    body: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details:
        body["error"]["details"] = details
    if request_id:
        body["request_id"] = request_id

    return JSONResponse(status_code=status_code, content=body)


def raise_error(
    status_code: int,
    code: str,
    message: str,
    details: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Raise an HTTPException with a standardized error body."""
    raise HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": message,
            **({"details": details} if details else {}),
        },
    )


def validation_error(message: str, details: Optional[List[Dict[str, Any]]] = None) -> None:
    raise_error(400, ErrorCode.VALIDATION_ERROR, message, details)


def not_found(message: str = "Resource not found") -> None:
    raise_error(404, ErrorCode.NOT_FOUND, message)


def unauthorized(message: str = "Authentication required") -> None:
    raise_error(401, ErrorCode.UNAUTHORIZED, message)


def forbidden(message: str = "Access denied") -> None:
    raise_error(403, ErrorCode.FORBIDDEN, message)


def ai_unavailable(message: str = "AI service is not configured") -> None:
    raise_error(503, ErrorCode.AI_SERVICE_UNAVAILABLE, message)


def ai_error(message: str = "AI service encountered an error") -> None:
    raise_error(500, ErrorCode.AI_SERVICE_ERROR, message)


def database_error(message: str = "Database is unavailable. Please try again later.") -> None:
    raise_error(503, ErrorCode.DATABASE_ERROR, message)


def file_too_large(max_mb: int = 5) -> None:
    raise_error(400, ErrorCode.FILE_TOO_LARGE, f"File too large. Maximum size is {max_mb}MB.")


def unsupported_file_type(ext: str, allowed: str = "PDF, DOCX, or TXT") -> None:
    raise_error(400, ErrorCode.UNSUPPORTED_FILE_TYPE, f"Unsupported file type: {ext}. Use {allowed}.")


def no_data(message: str = "No data found") -> JSONResponse:
    return error_response(404, ErrorCode.NO_DATA, message)


def internal_error(message: str = "Internal server error") -> None:
    raise_error(500, ErrorCode.INTERNAL_ERROR, message)
