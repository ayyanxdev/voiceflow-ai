"""Settings API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User

router = APIRouter(prefix="/api/settings", tags=["Settings"])
settings = get_settings()


class SettingsResponse(BaseModel):
    app_name: str
    app_env: str
    demo_mode: bool
    retell_configured: bool
    vapi_configured: bool
    google_configured: bool
    ai_provider_configured: bool


@router.get("", response_model=SettingsResponse, summary="Get application settings")
def get_app_settings(user: User = Depends(get_current_user)):
    return SettingsResponse(
        app_name=settings.APP_NAME,
        app_env=settings.APP_ENV,
        demo_mode=settings.is_demo_mode,
        retell_configured=settings.RETELL_API_KEY is not None,
        vapi_configured=settings.VAPI_API_KEY is not None,
        google_configured=settings.GOOGLE_CLIENT_ID is not None,
        ai_provider_configured=settings.OPENAI_API_KEY is not None,
    )
