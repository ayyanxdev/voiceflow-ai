"""FollowUp model."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True)
    type = Column(String(20), nullable=False)  # sms, email, call, manual
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, completed, failed
    message = Column(Text)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
