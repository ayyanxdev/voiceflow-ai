"""Lead model."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    phone = Column(String(30))
    email = Column(String(255))
    company = Column(String(200))
    source = Column(String(50), default="inbound_call")  # inbound_call, outbound, import, website, manual
    status = Column(String(30), default="new")  # new, contacted, qualified, unqualified, appointment_booked, follow_up, converted, lost
    temperature = Column(String(10), default="cold")  # cold, warm, hot
    notes = Column(Text)
    qualification_score = Column(Integer, default=0)  # 0-100
    assigned_to = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
