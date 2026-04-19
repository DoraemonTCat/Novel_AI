"""Rate limiting middleware using SlowAPI + Redis."""
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse


def get_rate_limit_key(request: Request) -> str:
    """
    Custom rate limit key function.
    Uses user_id from JWT if authenticated, otherwise falls back to IP.
    """
    user = getattr(request.state, "user", None)
    if user:
        return f"user:{user.id}"
    return get_remote_address(request)


# Create the limiter instance with Redis backend
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=["60/minute"],
    storage_uri="redis://redis:6379/1",
    strategy="fixed-window",
)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for 429 Too Many Requests."""
    retry_after = exc.detail.split("per")[0].strip() if exc.detail else "60"
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {exc.detail}",
            "retry_after": retry_after,
        },
        headers={"Retry-After": retry_after},
    )
