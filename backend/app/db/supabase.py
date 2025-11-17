"""
Supabase Database Client
Async Supabase client initialization and utilities
"""

from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global Supabase client
supabase_client: Client = None


async def init_supabase() -> Client:
    """Initialize Supabase client"""
    global supabase_client
    try:
        supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("Supabase client initialized successfully")
        return supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise


def get_supabase() -> Client:
    """Get Supabase client instance"""
    if supabase_client is None:
        raise RuntimeError("Supabase client not initialized. Call init_supabase() first.")
    return supabase_client


def get_supabase_service() -> Client:
    """Get Supabase service client with elevated permissions"""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )

