"""Structured logging configuration for CyberPath AI.

Provides JSON-formatted logs in production and human-readable logs in development.
Includes request context (request_id, user_id, method, path, status_code, duration).
"""
import json
import logging
import os
import sys
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Optional

request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        req_id = request_id_var.get()
        if req_id:
            log_entry["request_id"] = req_id

        uid = user_id_var.get()
        if uid:
            log_entry["user_id"] = uid

        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "path"):
            log_entry["path"] = record.path
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "client_ip"):
            log_entry["client_ip"] = record.client_ip

        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, default=str)


class HumanReadableFormatter(logging.Formatter):
    """Colored formatter for development readability."""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[1;31m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        req_id = request_id_var.get()
        prefix = f"[{req_id}] " if req_id else ""

        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        msg = f"{color}{ts} {record.levelname:8s}{self.RESET} {prefix}{record.name}: {record.getMessage()}"

        if record.exc_info and record.exc_info[0]:
            msg += f"\n{self.formatException(record.exc_info)}"

        return msg


def setup_logging(level: str = "INFO", json_output: bool = None):
    """Configure application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_output: Force JSON or human-readable. None = auto-detect from env.
    """
    if json_output is None:
        json_output = os.getenv("LOG_FORMAT", "json").lower() == "json"

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)

    if json_output:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(HumanReadableFormatter())

    root_logger.addHandler(handler)

    noisy_loggers = [
        "uvicorn.access",
        "uvicorn.error",
        "watchfiles",
        "httpcore",
        "httpx",
    ]
    for name in noisy_loggers:
        logging.getLogger(name).setLevel(logging.WARNING)
