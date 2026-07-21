import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from core.logging_config import request_id_var


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id_token = request_id_var.set(str(uuid.uuid4())[:8])
        start_time = time.time()

        client_ip = "unknown"
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client:
            client_ip = request.client.host

        logger = logging.getLogger("cyberpath.access")
        logger.info(
            "%s %s from %s",
            request.method,
            request.url.path,
            client_ip,
        )

        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        log_record = logging.LogRecord(
            name="cyberpath.access",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="%s %s -> %d (%sms)",
            args=(request.method, request.url.path, response.status_code, duration_ms),
            exc_info=None,
        )
        log_record.status_code = response.status_code
        log_record.method = request.method
        log_record.path = request.url.path
        log_record.duration_ms = duration_ms
        log_record.client_ip = client_ip
        logger.handle(log_record)

        response.headers["X-Request-ID"] = request_id_var.get() or ""
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        request_id_var.reset(req_id_token)
        return response
