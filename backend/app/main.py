"""Novel AI Backend — FastAPI Application Entry Point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db, close_db
from app.middleware.rate_limit import limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 Starting Novel AI Backend...")

    # Import all models for table creation
    import app.models  # noqa

    # Initialize database tables
    await init_db()
    logger.info("✅ Database initialized")

    yield

    # Shutdown
    await close_db()
    logger.info("👋 Novel AI Backend shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Novel AI",
    description="AI-Powered Novel Writing Platform — สร้างนิยายด้วย AI",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register API routes
from app.api.auth import router as auth_router
from app.api.novels import router as novels_router
from app.api.chapters import router as chapters_router
from app.api.characters import router as characters_router
from app.api.generation import router as generation_router
from app.api.websocket import router as ws_router
from app.api.export import router as export_router
from app.api.world import router as world_router

app.include_router(auth_router)
app.include_router(novels_router)
app.include_router(chapters_router)
app.include_router(characters_router)
app.include_router(generation_router)
app.include_router(ws_router)
app.include_router(export_router)
app.include_router(world_router)



@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "service": "Novel AI Backend",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    health = {"status": "healthy", "services": {}}

    # Check database
    try:
        from app.database import async_session_factory
        from sqlalchemy import text
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        health["services"]["database"] = "connected"
    except Exception as e:
        health["services"]["database"] = f"error: {str(e)}"
        health["status"] = "degraded"

    # Check Redis
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        health["services"]["redis"] = "connected"
    except Exception as e:
        health["services"]["redis"] = f"error: {str(e)}"
        health["status"] = "degraded"

    return health
