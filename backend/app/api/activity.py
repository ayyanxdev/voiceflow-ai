"""Activity API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.activity import Activity
from app.models.user import User

router = APIRouter(prefix="/api/activity", tags=["Activity"])


@router.get("", summary="Get activity log")
def list_activity(
    type_filter: Optional[str] = Query(None, alias="type"),
    entity_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Activity)
    if type_filter:
        query = query.filter(Activity.type == type_filter)
    if entity_type:
        query = query.filter(Activity.entity_type == entity_type)

    total = query.count()
    items = query.order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": a.id,
                "type": a.type,
                "description": a.description,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in items
        ],
    }
