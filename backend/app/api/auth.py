"""Auth API routes — Google OAuth + JWT endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.schemas.auth import TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.get("/google/login")
@limiter.limit("10/minute")
async def google_login(request: Request):
    """Redirect user to Google OAuth consent screen."""
    auth_url = AuthService.get_google_auth_url()
    return {"auth_url": auth_url}


@router.get("/google/callback")
@limiter.limit("10/minute")
async def google_callback(
    request: Request,
    code: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Google OAuth callback.
    Exchanges code for tokens, creates/updates user, returns JWT.
    """
    try:
        # Exchange authorization code for Google tokens
        google_tokens = await AuthService.exchange_code_for_tokens(code)
        google_access_token = google_tokens.get("access_token")

        if not google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token from Google",
            )

        # Get user info from Google
        user_info = await AuthService.get_google_user_info(google_access_token)

        # Create or update user in our database
        user = await AuthService.get_or_create_user(db, user_info)

        # Generate our JWT tokens
        access_token = AuthService.create_access_token(user.id, user.email)
        refresh_token = AuthService.create_refresh_token(user.id)

        # Save refresh token hash
        await AuthService.save_refresh_token(db, user, refresh_token)
        await db.commit()

        # Set refresh token as httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set True in production with HTTPS
            samesite="lax",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            path="/api/auth",
        )

        # Redirect to frontend with access token
        frontend_url = settings.FRONTEND_URL
        return Response(
            status_code=status.HTTP_302_FOUND,
            headers={
                "Location": f"{frontend_url}/auth/callback?token={access_token}"
            },
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with Google: {str(e)}",
        )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token from httpOnly cookie."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )

    result = await AuthService.refresh_access_token(db, refresh_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    return result


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Logout user — invalidate refresh token."""
    await AuthService.logout(db, str(current_user.id))
    await db.commit()

    response.delete_cookie(key="refresh_token", path="/api/auth")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user
