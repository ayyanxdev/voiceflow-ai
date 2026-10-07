"""Application configuration using Pydantic settings."""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "VoiceFlow AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite:///./voiceflow.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8000"

    # Retell AI
    RETELL_API_KEY: Optional[str] = None
    RETELL_AGENT_ID: Optional[str] = None
    RETELL_WEBHOOK_SECRET: Optional[str] = None

    # Vapi AI
    VAPI_API_KEY: Optional[str] = None
    VAPI_ASSISTANT_ID: Optional[str] = None
    VAPI_WEBHOOK_SECRET: Optional[str] = None

    # Google
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CALENDAR_ID: Optional[str] = None
    GOOGLE_SHEETS_ID: Optional[str] = None

    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None

    # Integrations
    CRM_API_KEY: Optional[str] = None
    CRM_WEBHOOK_URL: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None
    EMAIL_API_KEY: Optional[str] = None
    EMAIL_FROM_ADDRESS: Optional[str] = None

    # Demo Mode
    DEMO_MODE: bool = True

    @property
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode (no external APIs configured)."""
        return (
            self.RETELL_API_KEY is None
            and self.VAPI_API_KEY is None
            and self.APP_ENV == "development"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
