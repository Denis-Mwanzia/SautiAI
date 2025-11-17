"""
Application Configuration
Environment variables and settings management
"""

from pydantic_settings import BaseSettings
from typing import List, Union
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - can be comma-separated string or list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000"
    PRODUCTION_ORIGINS: Union[str, List[str]] = ""
    PUBLIC_BACKEND_ORIGIN: str = "http://localhost:8000"
    FRONTEND_ORIGINS: Union[str, List[str]] = "http://localhost:5173"
    CONNECT_SRC_EXTRA: Union[str, List[str]] = ""
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        sources = self.CORS_ORIGINS
        if self.ENVIRONMENT == "production" and self.PRODUCTION_ORIGINS:
            sources = self.PRODUCTION_ORIGINS
        if isinstance(sources, str):
            return [origin.strip() for origin in sources.split(",") if origin.strip()]
        return sources
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    DATABASE_URL: str
    
    # Google Cloud / Vertex AI
    VERTEX_AI_PROJECT: str
    VERTEX_AI_LOCATION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    
    # Twitter API
    TWITTER_BEARER_TOKEN: str = ""
    
    # Facebook Graph API
    FACEBOOK_ACCESS_TOKEN: str = ""
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    
    # Jaseci
    JASECI_SERVER_URL: str = "http://localhost:8000"
    JASECI_MASTER_KEY: str = ""
    
    # Monitoring
    SENTRY_DSN: str = ""

    # Feature flags
    ENABLE_AI: bool = False

    # Notifications
    SLACK_WEBHOOK_URL: str = ""
    ALERT_WEBHOOK_URL: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

