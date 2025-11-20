"""
Supabase Database Client
Async Supabase client initialization and utilities
"""

from supabase import create_client, Client
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Global Supabase client
supabase_client: Client = None


async def init_supabase() -> Client:
    """Initialize Supabase client"""
    global supabase_client
    try:
        # Ensure no proxy environment variables interfere
        # Cloud Run doesn't need proxy configuration
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
        original_proxy = {}
        for var in proxy_vars:
            if var in os.environ:
                original_proxy[var] = os.environ.pop(var)
        
        try:
            # Import ClientOptions for proper type
            from supabase.lib.client_options import ClientOptions
            
            # Create client with proper options object
            client_options = ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            )
            supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY,
                options=client_options
            )
            logger.info("Supabase client initialized successfully")
        except ImportError:
            # Fallback if ClientOptions not available - create without options
            logger.warning("ClientOptions not available, creating client without options")
            supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("Supabase client initialized successfully")
        finally:
            # Restore proxy environment variables if they existed
            for var, value in original_proxy.items():
                os.environ[var] = value
        
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
    # Ensure no proxy environment variables interfere
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
    original_proxy = {}
    for var in proxy_vars:
        if var in os.environ:
            original_proxy[var] = os.environ.pop(var)
    
    try:
        try:
            from supabase.lib.client_options import ClientOptions
            client_options = ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            )
            client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY,
                options=client_options
            )
        except ImportError:
            # Fallback if ClientOptions not available
            client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
    finally:
        # Restore proxy environment variables if they existed
        for var, value in original_proxy.items():
            os.environ[var] = value
    
    return client

