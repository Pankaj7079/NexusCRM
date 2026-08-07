"""Senior API Rate Limiter & Token Bucket Throttling Middleware."""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from nexuscrm.core.logging import logger


class TokenBucketRateLimiter:
    """Token Bucket Rate Limiter per client IP / user identity."""

    def __init__(self, requests_per_minute: int = 60, burst_limit: int = 10):
        self.rate = requests_per_minute / 60.0  # tokens per second
        self.capacity = burst_limit
        self.buckets: Dict[str, Tuple[float, float]] = {}  # ip -> (tokens, last_update_time)

    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """Check if request is permitted under rate limit capacity."""
        now = time.time()
        if client_id not in self.buckets:
            self.buckets[client_id] = (self.capacity - 1.0, now)
            return True, int(self.capacity - 1)

        tokens, last_update = self.buckets[client_id]
        # Replenish tokens based on elapsed time
        elapsed = now - last_update
        tokens = min(self.capacity, tokens + (elapsed * self.rate))

        if tokens >= 1.0:
            self.buckets[client_id] = (tokens - 1.0, now)
            return True, int(tokens - 1)
        else:
            self.buckets[client_id] = (tokens, now)
            retry_after = int((1.0 - tokens) / self.rate) + 1
            return False, retry_after


rate_limiter = TokenBucketRateLimiter(requests_per_minute=60, burst_limit=20)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI Middleware enforcing client rate limits and retry headers."""

    async def dispatch(self, request: Request, call_next):
        # Exclude static assets and health check from strict rate limits
        if request.url.path in ["/health", "/"] or request.url.path.startswith("/static"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        allowed, retry_after = rate_limiter.is_allowed(client_ip)

        if not allowed:
            logger.warning(f"RateLimitMiddleware: Client IP {client_ip} exceeded rate limit. Retry-After: {retry_after}s.")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response
