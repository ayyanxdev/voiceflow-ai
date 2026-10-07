"""Call model."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    external_call_id = Column(String(100), unique=True, nullable=True)
    direction = Column(String(10), nullable=False)  # inbound, outbound
    status = Column(String(20), default="initiated")  # initiated, ringing, answered, completed, failed, missed
    outcome = Column(String(30))  # qualified, unqualified, appointment_booked, callback_requested, transferred, no_answer, voicemail, not_interested, wrong_number, information_request, other
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer, default=0)
    recording_url = Column(String(500))
    transcript = Column(Text)
    summary = Column(Text)
    sentiment = Column(String(20))  # positive, neutral, negative
    qualification_score = Column(Integer, default=0)
    appointment_booked = Column(String(1), default="0")
    transferred_to_human = Column(String(1), default="0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
