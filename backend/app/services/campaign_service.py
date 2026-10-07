"""Campaign service."""

from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignLead
from app.models.activity import Activity
from app.schemas.campaign import CampaignCreate, CampaignUpdate


def create_campaign(db: Session, data: CampaignCreate, business_id: Optional[int] = None) -> Campaign:
    kwargs = data.model_dump()
    if business_id and not kwargs.get("business_id"):
        kwargs["business_id"] = business_id

    campaign = Campaign(**kwargs)
    db.add(campaign)
    db.flush()

    activity = Activity(
        business_id=campaign.business_id,
        type="campaign_created",
        description=f"Campaign created: {campaign.name}",
        entity_type="campaign",
        entity_id=campaign.id,
    )
    db.add(activity)
    db.commit()
    db.refresh(campaign)
    return campaign


def update_campaign(db: Session, campaign_id: int, data: CampaignUpdate) -> Optional[Campaign]:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return None

    update_data = data.model_dump(exclude_unset=True)
    old_status = campaign.status
    new_status = update_data.get("status")

    for field, value in update_data.items():
        setattr(campaign, field, value)

    if new_status and new_status != old_status:
        activity = Activity(
            business_id=campaign.business_id,
            type=f"campaign_{new_status}",
            description=f"Campaign {new_status}: {campaign.name}",
            entity_type="campaign",
            entity_id=campaign.id,
        )
        db.add(activity)

    db.commit()
    db.refresh(campaign)
    return campaign


def get_campaign(db: Session, campaign_id: int) -> Optional[Campaign]:
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()


def get_campaigns(
    db: Session,
    business_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Campaign], int]:
    query = db.query(Campaign)
    if business_id:
        query = query.filter(Campaign.business_id == business_id)
    if status:
        query = query.filter(Campaign.status == status)

    total = query.count()
    campaigns = query.order_by(desc(Campaign.created_at)).offset(skip).limit(limit).all()
    return campaigns, total


def add_leads_to_campaign(db: Session, campaign_id: int, lead_ids: list[int]) -> int:
    """Add leads to a campaign. Returns count added."""
    added = 0
    for lead_id in lead_ids:
        existing = (
            db.query(CampaignLead)
            .filter(CampaignLead.campaign_id == campaign_id, CampaignLead.lead_id == lead_id)
            .first()
        )
        if not existing:
            cl = CampaignLead(campaign_id=campaign_id, lead_id=lead_id)
            db.add(cl)
            added += 1

    if added > 0:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.total_leads += added
        db.commit()

    return added
