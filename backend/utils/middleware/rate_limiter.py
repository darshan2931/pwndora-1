import time
from collections import defaultdict
from typing import Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst: int = 10,
    ):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.burst = burst
        self._hits: Dict[str, list[float]] = defaultdict(list)

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _prune(self, ip: str, now: float) -> None:
        cutoff = now - 60.0
        self._hits[ip] = [t for t in self._hits[ip] if t > cutoff]

    def _is_limited(self, ip: str) -> Tuple[bool, int]:
        now = time.time()
        self._prune(ip, now)
        hits = self._hits[ip]

        if len(hits) >= self.rpm:
            retry_after = int(60 - (now - hits[0])) + 1
            return True, retry_after

        if len(hits) >= self.burst:
            recent = [t for t in hits if now - t < 1.0]
            if len(recent) >= self.burst:
                return True, 1

        return False, 0

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        ip = self._client_ip(request)
        limited, retry_after = self._is_limited(ip)

        if limited:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Rate limit exceeded. Try again later.",
                    "errors": [f"Retry after {retry_after}s"],
                },
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        if response.status_code < 500:
            self._hits[ip].append(time.time())
        return response
