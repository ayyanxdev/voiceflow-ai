"""Demo mode API endpoints for generating sample data."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import log
from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.demo.seed_data import seed_demo_data

router = APIRouter(prefix="/api/demo", tags=["Demo"])


@router.post("/seed", summary="Generate demo data for the dashboard")
def generate_demo_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Seed the database with realistic demo data."""
    result = seed_demo_data(db)
    return result


# Tables in FK-safe deletion order (children first)
_CLEAR_TABLES = [
    "activities",
    "appointments",
    "followups",
    "campaign_leads",
    "campaigns",
    "calls",
    "leads",
    "businesses",
]


@router.post("/clear", summary="Delete all data (except admin user) for a clean slate")
def clear_all_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Truncate every table except users so the dashboard reflects only real data.

    The admin user is preserved so you can still log in.
    """
    deleted = {}
    for table in _CLEAR_TABLES:
        result = db.execute(text(f"DELETE FROM {table}"))
        deleted[table] = result.rowcount
    db.commit()

    log.info("Demo data cleared: %s", deleted)
    return {"message": "All data deleted (admin user preserved)", "deleted": deleted}
