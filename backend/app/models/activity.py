"""Activity model for audit/activity log."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    type = Column(String(50), nullable=False)  # call_received, call_completed, lead_created, lead_updated, appointment_booked, appointment_cancelled, campaign_started, campaign_paused, follow_up_scheduled, crm_sync, webhook_received, etc.
    description = Column(Text, nullable=False)
    entity_type = Column(String(50))  # lead, call, appointment, campaign, followup
    entity_id = Column(Integer)
    metadata_json = Column(Text)  # JSON string for extra data
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
