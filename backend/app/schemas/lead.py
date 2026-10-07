"""Lead Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeadBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    source: str = "manual"
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    business_id: Optional[int] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    temperature: Optional[str] = None
    notes: Optional[str] = None
    qualification_score: Optional[int] = None
    assigned_to: Optional[int] = None


class LeadResponse(LeadBase):
    id: int
    business_id: Optional[int] = None
    status: str
    temperature: str
    qualification_score: int
    assigned_to: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
