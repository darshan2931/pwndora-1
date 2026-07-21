"""In-memory TTL cache utilities for CyberPath AI.

Provides a simple TTLCache class and a @cached decorator for caching
expensive function results in memory.
"""
import functools
import hashlib
import json
import logging
import threading
import time
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class TTLCache:
    """Thread-safe in-memory cache with per-entry TTL expiration."""

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._store:
                return None
            value, expiry = self._store[key]
            if time.time() > expiry:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            if len(self._store) >= self._max_size and key not in self._store:
                self._evict_oldest()
            self._store[key] = (value, time.time() + (ttl or self._default_ttl))

    def invalidate(self, key: str) -> bool:
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def invalidate_prefix(self, prefix: str) -> int:
        with self._lock:
            keys_to_delete = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._store[k]
            return len(keys_to_delete)

    def clear(self) -> int:
        with self._lock:
            count = len(self._store)
            self._store.clear()
            return count

    def size(self) -> int:
        with self._lock:
            now = time.time()
            expired = [k for k, (_, exp) in self._store.items() if now > exp]
            for k in expired:
                del self._store[k]
            return len(self._store)

    def _evict_oldest(self) -> None:
        if not self._store:
            return
        oldest_key = min(self._store, key=lambda k: self._store[k][1])
        del self._store[oldest_key]


_global_cache = TTLCache(default_ttl=300, max_size=1000)


def get_cache() -> TTLCache:
    return _global_cache


def make_cache_key(*args, **kwargs) -> str:
    """Generate a deterministic cache key from function arguments."""
    parts = [str(a) for a in args]
    parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    raw = ":".join(parts)
    return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()


def cached(
    ttl: int = 300,
    prefix: str = "",
    cache: Optional[TTLCache] = None,
) -> Callable:
    """Decorator that caches function return values in memory.

    Args:
        ttl: Time-to-live in seconds.
        prefix: Cache key prefix for group invalidation.
        cache: Custom cache instance. Uses global cache if None.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            c = cache or _global_cache
            key = f"{prefix}:{func.__name__}:{make_cache_key(*args, **kwargs)}"
            result = c.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            if result is not None:
                c.set(key, result, ttl)
            return result

        wrapper.invalidate = lambda *a, **kw: (
            (cache or _global_cache).invalidate(
                f"{prefix}:{func.__name__}:{make_cache_key(*a, **kw)}"
            )
        )
        wrapper.invalidate_prefix = lambda: (
            (cache or _global_cache).invalidate_prefix(f"{prefix}:{func.__name__}:")
        )
        return wrapper
    return decorator
