"""Novel AI Backend - Configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # === Google OAuth 2.0 ===
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # === JWT Security ===
    JWT_SECRET_KEY: str = "change-me-to-a-random-64-char-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # === AI Providers ===
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "models/gemini-2.5-flash"
    OLLAMA_HOST: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3:8b"

    # === Database ===
    DATABASE_URL: str = "postgresql+asyncpg://novel_user:novel_pass_change_me@postgres:5432/novel_ai"

    # === Redis ===
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_RATE_LIMIT_URL: str = "redis://redis:6379/1"

    # === ChromaDB ===
    CHROMA_HOST: str = "http://chromadb:8000"

    # === Stable Diffusion ===
    SD_API_URL: str = "http://stable-diffusion:7860"

    # === App Settings ===
    CORS_ORIGINS: str = "http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
