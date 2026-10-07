"""VoiceFlow AI — Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import log
from app.core.security import hash_password, verify_password
from app.database.database import init_db
from app.models.user import User
from app.database.database import SessionLocal
from app.api import auth, leads, calls, appointments, campaigns, dashboard, webhooks, activity, settings as settings_api, demo
from app.api.websocket import router as ws_router
from app.api.export import router as export_router

settings = get_settings()


DEMO_ADMIN_EMAIL = "admin@voiceflow.ai"
DEMO_ADMIN_PASSWORD = "admin123"


def _seed_admin_user():
    """Create or repair the demo admin user. Idempotent.

    - If the admin user does not exist, create it.
    - If it exists but the password hash cannot be verified
      (e.g. corrupted or hashed with an incompatible bcrypt version),
      update the hash so the documented demo credentials always work.
    - Existing valid users are never duplicated.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == DEMO_ADMIN_EMAIL).first()
        if user is None:
            user = User(
                name="Admin User",
                email=DEMO_ADMIN_EMAIL,
                password_hash=hash_password(DEMO_ADMIN_PASSWORD),
                role="admin",
                is_active="1",
            )
            db.add(user)
            db.commit()
            log.info("Admin user created: %s", DEMO_ADMIN_EMAIL)
        elif not verify_password(DEMO_ADMIN_PASSWORD, user.password_hash):
            log.warning(
                "Admin user exists but password hash is invalid — updating"
            )
            user.password_hash = hash_password(DEMO_ADMIN_PASSWORD)
            db.commit()
            log.info("Admin password hash updated")
        else:
            log.info("Admin user seed check passed (already valid)")
    except Exception:
        db.rollback()
        log.exception("Failed to seed admin user")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events."""
    log.info("Starting VoiceFlow AI v%s (%s)", settings.APP_VERSION, settings.APP_ENV)
    init_db()
    log.info("Database initialized")
    _seed_admin_user()
    log.info("Admin user seed check complete")
    yield
    log.info("VoiceFlow AI shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Voice Sales & Receptionist Automation Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(leads.router)
app.include_router(calls.router)
app.include_router(appointments.router)
app.include_router(campaigns.router)
app.include_router(activity.router)
app.include_router(webhooks.router)
app.include_router(settings_api.router)
app.include_router(demo.router)
app.include_router(ws_router)
app.include_router(export_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
