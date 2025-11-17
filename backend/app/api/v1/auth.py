"""
Authentication Endpoints
Endpoints for user authentication via Supabase Auth
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging

from app.models.schemas import APIResponse, UserProfile
from app.services.auth_service import AuthService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_auth_service() -> AuthService:
    """Dependency injection for AuthService"""
    return AuthService()


@router.get("/profile", response_model=APIResponse)
async def get_profile(
    token: str,
    service: AuthService = Depends(get_auth_service)
):
    """Get user profile from Supabase Auth"""
    try:
        profile = await service.get_user_profile(token)
        return APIResponse(
            success=True,
            message="Profile retrieved",
            data=profile
        )
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/verify", response_model=APIResponse)
async def verify_token(
    token: str,
    service: AuthService = Depends(get_auth_service)
):
    """Verify authentication token"""
    try:
        is_valid = await service.verify_token(token)
        return APIResponse(
            success=is_valid,
            message="Token verified" if is_valid else "Token invalid"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")

