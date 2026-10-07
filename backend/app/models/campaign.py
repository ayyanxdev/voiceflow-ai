"""Campaign and CampaignLead models."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="draft")  # draft, active, paused, completed
    total_leads = Column(Integer, default=0)
    completed_calls = Column(Integer, default=0)
    qualified_leads = Column(Integer, default=0)
    appointments = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class CampaignLead(Base):
    __tablename__ = "campaign_leads"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, calling, completed, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
