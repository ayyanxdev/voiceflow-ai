"""Follow-up service."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.followup import FollowUp
from app.models.activity import Activity


def create_followup(
    db: Session,
    lead_id: int,
    followup_type: str = "call",
    message: str = "",
    scheduled_at: Optional[datetime] = None,
    business_id: Optional[int] = None,
    call_id: Optional[int] = None,
) -> FollowUp:
    """Create a follow-up record."""
    if not scheduled_at:
        scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)

    followup = FollowUp(
        business_id=business_id,
        lead_id=lead_id,
        call_id=call_id,
        type=followup_type,
        scheduled_at=scheduled_at,
        message=message,
    )
    db.add(followup)
    db.flush()

    activity = Activity(
        business_id=business_id,
        type="follow_up_scheduled",
        description=f"Follow-up scheduled ({followup_type})",
        entity_type="followup",
        entity_id=followup.id,
    )
    db.add(activity)
    db.commit()
    db.refresh(followup)
    return followup


def get_followups(
    db: Session,
    lead_id: Optional[int] = None,
    business_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[FollowUp], int]:
    """Get follow-ups with filtering."""
    query = db.query(FollowUp)
    if lead_id:
        query = query.filter(FollowUp.lead_id == lead_id)
    if business_id:
        query = query.filter(FollowUp.business_id == business_id)
    if status:
        query = query.filter(FollowUp.status == status)

    total = query.count()
    items = query.order_by(desc(FollowUp.scheduled_at)).offset(skip).limit(limit).all()
    return items, total


def update_followup_status(
    db: Session, followup_id: int, new_status: str
) -> Optional[FollowUp]:
    """Update follow-up status."""
    fu = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not fu:
        return None
    fu.status = new_status
    if new_status in ("completed", "sent"):
        fu.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(fu)
    return fu
