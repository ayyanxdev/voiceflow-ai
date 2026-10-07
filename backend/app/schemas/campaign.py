"""Campaign Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None


class CampaignCreate(CampaignBase):
    business_id: Optional[int] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CampaignResponse(CampaignBase):
    id: int
    business_id: Optional[int] = None
    status: str
    total_leads: int
    completed_calls: int
    qualified_leads: int
    appointments: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
