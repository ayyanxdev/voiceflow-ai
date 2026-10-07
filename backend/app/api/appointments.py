"""Appointments API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.services import appointment_service

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.get("", response_model=list[AppointmentResponse], summary="List appointments")
def list_appointments(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    upcoming_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appts, total = appointment_service.get_appointments(
        db, status=status_filter, search=search, upcoming_only=upcoming_only,
        skip=skip, limit=limit
    )
    return [AppointmentResponse.model_validate(a) for a in appts]


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED, summary="Create appointment")
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appt = appointment_service.create_appointment(db, data)
    return AppointmentResponse.model_validate(appt)


@router.put("/{appointment_id}", response_model=AppointmentResponse, summary="Update appointment")
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appt = appointment_service.update_appointment(db, appointment_id, data)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentResponse.model_validate(appt)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Cancel appointment")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not appointment_service.delete_appointment(db, appointment_id):
        raise HTTPException(status_code=404, detail="Appointment not found")
