"""Business Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BusinessBase(BaseModel):
    name: str
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    timezone: str = "UTC"
    business_hours: Optional[str] = None
    description: Optional[str] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    timezone: Optional[str] = None
    business_hours: Optional[str] = None
    description: Optional[str] = None


class BusinessResponse(BusinessBase):
    id: int
    owner_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
