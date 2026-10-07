"""Call Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CallBase(BaseModel):
    direction: str
    business_id: Optional[int] = None
    lead_id: Optional[int] = None


class CallCreate(CallBase):
    external_call_id: Optional[str] = None


class CallUpdate(BaseModel):
    status: Optional[str] = None
    outcome: Optional[str] = None
    duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    qualification_score: Optional[int] = None
    appointment_booked: Optional[str] = None
    transferred_to_human: Optional[str] = None
    external_call_id: Optional[str] = None


class CallResponse(CallBase):
    id: int
    external_call_id: Optional[str] = None
    status: str
    outcome: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    qualification_score: int
    appointment_booked: str
    transferred_to_human: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
