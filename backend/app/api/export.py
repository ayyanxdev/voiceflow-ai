"""CSV export endpoints."""

import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.call import Call
from app.models.lead import Lead
from app.models.appointment import Appointment

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/calls", summary="Export calls as CSV")
def export_calls(
    direction: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    outcome: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Call)
    if direction:
        query = query.filter(Call.direction == direction)
    if status_filter:
        query = query.filter(Call.status == status_filter)
    if outcome:
        query = query.filter(Call.outcome == outcome)
    
    calls = query.order_by(Call.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Direction', 'Status', 'Outcome', 'Duration (s)',
        'Score', 'Sentiment', 'Appointment Booked', 'Created At'
    ])
    for c in calls:
        writer.writerow([
            c.id, c.direction, c.status, c.outcome, c.duration_seconds,
            c.qualification_score, c.sentiment, c.appointment_booked,
            c.created_at.isoformat() if c.created_at else ''
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=calls_export.csv"}
    )


@router.get("/leads", summary="Export leads as CSV")
def export_leads(
    status_filter: Optional[str] = Query(None, alias="status"),
    temperature: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Lead)
    if status_filter:
        query = query.filter(Lead.status == status_filter)
    if temperature:
        query = query.filter(Lead.temperature == temperature)
    
    leads = query.order_by(Lead.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'First Name', 'Last Name', 'Phone', 'Email',
        'Company', 'Source', 'Status', 'Temperature', 'Score',
        'Notes', 'Created At'
    ])
    for l in leads:
        writer.writerow([
            l.id, l.first_name, l.last_name, l.phone, l.email,
            l.company, l.source, l.status, l.temperature,
            l.qualification_score, l.notes,
            l.created_at.isoformat() if l.created_at else ''
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )


@router.get("/appointments", summary="Export appointments as CSV")
def export_appointments(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Appointment)
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    appointments = query.order_by(Appointment.start_time.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Title', 'Customer Name', 'Phone', 'Email',
        'Status', 'Start Time', 'End Time', 'Notes', 'Created At'
    ])
    for a in appointments:
        writer.writerow([
            a.id, a.title, a.customer_name, a.customer_phone,
            a.customer_email, a.status,
            a.start_time.isoformat() if a.start_time else '',
            a.end_time.isoformat() if a.end_time else '',
            a.notes,
            a.created_at.isoformat() if a.created_at else ''
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=appointments_export.csv"}
    )
