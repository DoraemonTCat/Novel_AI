"""Authentication service — Google OAuth 2.0 + JWT management."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import httpx
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.auth import GoogleUserInfo, TokenResponse


# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_SCOPES = "openid email profile"


class AuthService:
    """Handles Google OAuth flow and JWT token management."""

    @staticmethod
    def get_google_auth_url() -> str:
        """Generate Google OAuth consent screen URL."""
        params = {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": GOOGLE_SCOPES,
            "access_type": "offline",
            "prompt": "consent",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{GOOGLE_AUTH_URL}?{query}"

    @staticmethod
    async def exchange_code_for_tokens(code: str) -> dict:
        """Exchange authorization code for Google tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_google_user_info(access_token: str) -> GoogleUserInfo:
        """Fetch user profile from Google."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return GoogleUserInfo(
                google_id=data["id"],
                email=data["email"],
                name=data.get("name", data["email"]),
                avatar_url=data.get("picture"),
            )

    @staticmethod
    async def get_or_create_user(db: AsyncSession, user_info: GoogleUserInfo) -> User:
        """Find existing user by Google ID or create a new one."""
        result = await db.execute(
            select(User).where(User.google_id == user_info.google_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Update last login and any changed profile info
            user.last_login = datetime.now(timezone.utc)
            user.name = user_info.name
            user.avatar_url = user_info.avatar_url
            await db.flush()
            return user

        # Create new user
        user = User(
            email=user_info.email,
            name=user_info.name,
            avatar_url=user_info.avatar_url,
            google_id=user_info.google_id,
        )
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    def create_access_token(user_id: UUID, email: str) -> str:
        """Create a short-lived JWT access token."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: UUID) -> str:
        """Create a long-lived JWT refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh",
            "jti": secrets.token_hex(16),  # Unique token ID
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a refresh token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    async def save_refresh_token(db: AsyncSession, user: User, refresh_token: str) -> None:
        """Save hashed refresh token to user record."""
        user.refresh_token_hash = AuthService.hash_token(refresh_token)
        await db.flush()

    @staticmethod
    def verify_token(token: str, expected_type: str = "access") -> Optional[dict]:
        """Verify and decode a JWT token. Returns payload or None."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != expected_type:
                return None
            return payload
        except JWTError:
            return None

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession, refresh_token: str
    ) -> Optional[TokenResponse]:
        """Validate refresh token and issue new access token."""
        payload = AuthService.verify_token(refresh_token, expected_type="refresh")
        if not payload:
            return None

        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        # Verify stored hash matches
        if user.refresh_token_hash != AuthService.hash_token(refresh_token):
            return None

        # Issue new access token
        new_access_token = AuthService.create_access_token(user.id, user.email)
        return TokenResponse(
            access_token=new_access_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    async def logout(db: AsyncSession, user_id: str) -> None:
        """Invalidate refresh token by clearing the hash."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.refresh_token_hash = None
            await db.flush()
