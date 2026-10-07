"""Appointment Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RetellBookAppointment(BaseModel):
    """Request body for Retell AI custom-function: book an appointment.

    All fields are strings because Retell passes function-call arguments
    as strings.  The endpoint converts them before persisting.
    """

    customer_name: str = Field(..., description="Full name of the customer")
    customer_phone: str = Field(..., description="Customer phone number")
    start_time: str = Field(..., description="Appointment start time (ISO 8601)")
    title: str = Field(default="", description="Appointment title / reason")
    customer_email: Optional[str] = Field(default=None, description="Customer email")
    end_time: Optional[str] = Field(default=None, description="Appointment end time (ISO 8601)")
    notes: Optional[str] = Field(default=None, description="Free-text notes")
    lead_id: Optional[int] = Field(default=None, description="Existing lead ID to link")
    call_id: Optional[int] = Field(default=None, description="Existing call ID to link")
    business_id: Optional[int] = Field(default=None, description="Business ID")


class AppointmentBase(BaseModel):
    title: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    business_id: Optional[int] = None
    lead_id: Optional[int] = None
    call_id: Optional[int] = None


class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    id: int
    business_id: Optional[int] = None
    lead_id: Optional[int] = None
    call_id: Optional[int] = None
    status: str
    calendar_event_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
