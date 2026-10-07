"""Appointment service."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.activity import Activity
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


def create_appointment(
    db: Session,
    data: AppointmentCreate,
    business_id: Optional[int] = None,
) -> Appointment:
    """Create a new appointment."""
    kwargs = data.model_dump()
    if business_id and not kwargs.get("business_id"):
        kwargs["business_id"] = business_id

    appointment = Appointment(**kwargs)
    db.add(appointment)
    db.flush()

    activity = Activity(
        business_id=appointment.business_id,
        type="appointment_booked",
        description=f"Appointment booked: {appointment.title} for {appointment.customer_name or 'customer'}",
        entity_type="appointment",
        entity_id=appointment.id,
    )
    db.add(activity)
    db.commit()
    db.refresh(appointment)
    return appointment


def update_appointment(
    db: Session, appointment_id: int, data: AppointmentUpdate
) -> Optional[Appointment]:
    """Update an appointment."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Track status change for activity
    old_status = appointment.status
    new_status = update_data.get("status")

    for field, value in update_data.items():
        setattr(appointment, field, value)

    if new_status and new_status != old_status:
        activity = Activity(
            business_id=appointment.business_id,
            type=f"appointment_{new_status}",
            description=f"Appointment {new_status}: {appointment.title}",
            entity_type="appointment",
            entity_id=appointment.id,
        )
        db.add(activity)

    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def get_appointments(
    db: Session,
    business_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    upcoming_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Appointment], int]:
    """Get appointments with filtering."""
    query = db.query(Appointment)

    if business_id:
        query = query.filter(Appointment.business_id == business_id)
    if status:
        query = query.filter(Appointment.status == status)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Appointment.customer_name.ilike(s))
            | (Appointment.title.ilike(s))
            | (Appointment.customer_phone.ilike(s))
        )
    if upcoming_only:
        query = query.filter(Appointment.start_time >= datetime.now(timezone.utc))
        query = query.filter(Appointment.status.in_(["scheduled", "confirmed"]))

    total = query.count()
    appointments = query.order_by(desc(Appointment.start_time)).offset(skip).limit(limit).all()
    return appointments, total


def delete_appointment(db: Session, appointment_id: int) -> bool:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return False

    appointment.status = "cancelled"
    activity = Activity(
        business_id=appointment.business_id,
        type="appointment_cancelled",
        description=f"Appointment cancelled: {appointment.title}",
        entity_type="appointment",
        entity_id=appointment.id,
    )
    db.add(activity)
    db.commit()
    return True
