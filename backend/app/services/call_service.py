"""Call service."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.call import Call
from app.models.activity import Activity
from app.schemas.call import CallCreate, CallUpdate


def create_call(db: Session, call_data: CallCreate, business_id: Optional[int] = None) -> Call:
    """Create a new call record."""
    data = call_data.model_dump()
    if business_id and not data.get("business_id"):
        data["business_id"] = business_id

    call = Call(**data, status="initiated", started_at=datetime.now(timezone.utc))
    db.add(call)
    db.flush()

    activity = Activity(
        business_id=call.business_id,
        type="call_received" if call.direction == "inbound" else "call_initiated",
        description=f"{'Inbound' if call.direction == 'inbound' else 'Outbound'} call initiated",
        entity_type="call",
        entity_id=call.id,
    )
    db.add(activity)
    db.commit()
    db.refresh(call)
    return call


def update_call(db: Session, call_id: int, call_data: CallUpdate) -> Optional[Call]:
    """Update a call record."""
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        return None

    update_data = call_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(call, field, value)

    # Auto-set end time when completed (only if duration not already provided)
    if call.status == "completed" and not call.ended_at:
        call.ended_at = datetime.now(timezone.utc)
        # Only auto-calculate duration when the caller did NOT supply one
        if call.started_at and "duration_seconds" not in update_data:
            started = call.started_at.replace(tzinfo=timezone.utc) if call.started_at.tzinfo is None else call.started_at
            ended = call.ended_at
            call.duration_seconds = int((ended - started).total_seconds())

    db.commit()
    db.refresh(call)
    return call


def get_call(db: Session, call_id: int) -> Optional[Call]:
    return db.query(Call).filter(Call.id == call_id).first()


def get_call_by_external_id(db: Session, external_id: str) -> Optional[Call]:
    return db.query(Call).filter(Call.external_call_id == external_id).first()


def get_calls(
    db: Session,
    business_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    direction: Optional[str] = None,
    status: Optional[str] = None,
    outcome: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Call], int]:
    """Get calls with filtering and pagination."""
    query = db.query(Call)

    if business_id:
        query = query.filter(Call.business_id == business_id)
    if lead_id:
        query = query.filter(Call.lead_id == lead_id)
    if direction:
        query = query.filter(Call.direction == direction)
    if status:
        query = query.filter(Call.status == status)
    if outcome:
        query = query.filter(Call.outcome == outcome)
    if search:
        query = query.filter(
            (Call.transcript.ilike(f"%{search}%"))
            | (Call.summary.ilike(f"%{search}%"))
        )

    total = query.count()
    calls = query.order_by(desc(Call.created_at)).offset(skip).limit(limit).all()
    return calls, total
