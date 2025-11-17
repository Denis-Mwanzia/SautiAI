"""
Authentication Service
Service for Supabase Auth integration
"""

import logging
from typing import Dict, Any

from app.db.supabase import get_supabase
from app.models.schemas import UserProfile

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    async def get_user_profile(self, token: str) -> Dict[str, Any]:
        """
        Get user profile from Supabase Auth
        
        Args:
            token: Supabase JWT token
        """
        try:
            # Verify token and get user
            user = self.supabase.auth.get_user(token)
            
            if not user:
                raise ValueError("Invalid token")
            
            return {
                "id": user.user.id,
                "email": user.user.email,
                "created_at": user.user.created_at
            }
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise
    
    async def verify_token(self, token: str) -> bool:
        """Verify authentication token"""
        try:
            user = self.supabase.auth.get_user(token)
            return user is not None
        except:
            return False

