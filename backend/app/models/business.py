"""Business model."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    industry = Column(String(100))
    phone = Column(String(30))
    email = Column(String(255))
    website = Column(String(255))
    address = Column(Text)
    timezone = Column(String(50), default="UTC")
    business_hours = Column(Text)  # JSON string
    description = Column(Text)
    owner_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
