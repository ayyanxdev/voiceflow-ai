"""Lead service with scoring and qualification logic."""

from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.activity import Activity
from app.schemas.lead import LeadCreate, LeadUpdate


def calculate_temperature(score: int) -> str:
    """Calculate lead temperature from qualification score."""
    if score >= 70:
        return "hot"
    elif score >= 40:
        return "warm"
    return "cold"


def calculate_qualification_score(lead_data: dict) -> int:
    """
    Calculate qualification score based on available data.

    Scoring:
    +20 if interested (has phone or email = contactable)
    +20 if requested pricing / has budget info
    +30 if appointment requested
    +20 if qualified (has status == qualified)
    +10 if gave complete contact details (phone + email)
    Normalized to 0-100.
    """
    score = 0

    # Contactable
    if lead_data.get("phone") or lead_data.get("email"):
        score += 20

    # Complete contact details
    if lead_data.get("phone") and lead_data.get("email"):
        score += 10

    # Has company info (more serious lead)
    if lead_data.get("company"):
        score += 10

    # Notes indicate interest
    notes = (lead_data.get("notes") or "").lower()
    if any(kw in notes for kw in ["interested", "pricing", "budget", "ready"]):
        score += 20

    if any(kw in notes for kw in ["appointment", "schedule", "meeting"]):
        score += 30

    if lead_data.get("status") == "qualified":
        score += 20

    return min(score, 100)


def create_lead(db: Session, lead_data: LeadCreate, business_id: Optional[int] = None) -> Lead:
    """Create a new lead."""
    data = lead_data.model_dump()
    if business_id and not data.get("business_id"):
        data["business_id"] = business_id

    score = calculate_qualification_score(data)
    temperature = calculate_temperature(score)

    lead = Lead(**data, qualification_score=score, temperature=temperature)
    db.add(lead)
    db.flush()

    # Log activity
    activity = Activity(
        business_id=lead.business_id,
        type="lead_created",
        description=f"New lead created: {lead.first_name} {lead.last_name or ''}",
        entity_type="lead",
        entity_id=lead.id,
    )
    db.add(activity)
    db.commit()
    db.refresh(lead)
    return lead


def update_lead(db: Session, lead_id: int, lead_data: LeadUpdate) -> Optional[Lead]:
    """Update an existing lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None

    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    # Recalculate score
    lead_dict = {c.name: getattr(lead, c.name) for c in Lead.__table__.columns}
    lead.qualification_score = calculate_qualification_score(lead_dict)
    lead.temperature = calculate_temperature(lead.qualification_score)

    # Log activity
    activity = Activity(
        business_id=lead.business_id,
        type="lead_updated",
        description=f"Lead updated: {lead.first_name} {lead.last_name or ''}",
        entity_type="lead",
        entity_id=lead.id,
    )
    db.add(activity)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_leads(
    db: Session,
    business_id: Optional[int] = None,
    status: Optional[str] = None,
    temperature: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Lead], int]:
    """Get leads with filtering and pagination."""
    query = db.query(Lead)

    if business_id:
        query = query.filter(Lead.business_id == business_id)
    if status:
        query = query.filter(Lead.status == status)
    if temperature:
        query = query.filter(Lead.temperature == temperature)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Lead.first_name.ilike(search_filter))
            | (Lead.last_name.ilike(search_filter))
            | (Lead.email.ilike(search_filter))
            | (Lead.phone.ilike(search_filter))
            | (Lead.company.ilike(search_filter))
        )

    total = query.count()
    leads = query.order_by(desc(Lead.created_at)).offset(skip).limit(limit).all()
    return leads, total


def delete_lead(db: Session, lead_id: int) -> bool:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return False
    db.delete(lead)
    db.commit()
    return True
