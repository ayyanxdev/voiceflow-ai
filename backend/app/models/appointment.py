"""Appointment model."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True)
    title = Column(String(200), nullable=False)
    customer_name = Column(String(200))
    customer_phone = Column(String(30))
    customer_email = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20), default="scheduled")  # scheduled, confirmed, completed, cancelled, rescheduled, no_show
    calendar_event_id = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
