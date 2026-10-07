"""Dashboard service for aggregating KPIs and chart data."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.call import Call
from app.models.lead import Lead
from app.models.appointment import Appointment
from app.models.activity import Activity
from app.schemas.dashboard import (
    DashboardChartData,
    DashboardOverview,
    DashboardResponse,
    ActivityItem,
    CallsOverTime,
    CallOutcome,
    LeadFunnelItem,
)


def get_overview(db: Session, business_id: Optional[int] = None) -> DashboardOverview:
    """Get dashboard KPI overview."""
    base_call = db.query(Call)
    base_lead = db.query(Lead)
    base_appt = db.query(Appointment)

    if business_id:
        base_call = base_call.filter(Call.business_id == business_id)
        base_lead = base_lead.filter(Lead.business_id == business_id)
        base_appt = base_appt.filter(Appointment.business_id == business_id)

    total_calls = base_call.count()
    answered_calls = base_call.filter(
        Call.status.in_(["completed"])
    ).count()
    total_leads = base_lead.count()
    qualified_leads = base_lead.filter(Lead.status == "qualified").count()
    appointments_booked = base_appt.count()
    hot_leads = base_lead.filter(Lead.temperature == "hot").count()

    conversion_rate = 0.0
    if total_calls > 0:
        conversion_rate = round((appointments_booked / total_calls) * 100, 1)

    avg_duration = 0.0
    avg_result = db.query(func.avg(Call.duration_seconds)).filter(
        Call.duration_seconds > 0
    )
    if business_id:
        avg_result = avg_result.filter(Call.business_id == business_id)
    avg_val = avg_result.scalar()
    if avg_val:
        avg_duration = round(float(avg_val), 1)

    return DashboardOverview(
        total_calls=total_calls,
        answered_calls=answered_calls,
        qualified_leads=qualified_leads,
        appointments_booked=appointments_booked,
        conversion_rate=conversion_rate,
        avg_call_duration=avg_duration,
        total_leads=total_leads,
        hot_leads=hot_leads,
    )


def get_charts(db: Session, business_id: Optional[int] = None) -> DashboardChartData:
    """Get chart data for the dashboard."""
    now = datetime.now(timezone.utc)

    # Calls over last 30 days
    calls_over_time = []
    for i in range(29, -1, -1):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        day_start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        q = db.query(func.count(Call.id)).filter(
            Call.created_at >= day_start, Call.created_at < day_end
        )
        if business_id:
            q = q.filter(Call.business_id == business_id)
        count = q.scalar() or 0

        calls_over_time.append(CallsOverTime(date=day, count=count))

    # Call outcomes
    outcome_query = db.query(
        Call.outcome, func.count(Call.id)
    ).group_by(Call.outcome)
    if business_id:
        outcome_query = outcome_query.filter(Call.business_id == business_id)
    call_outcomes = [
        CallOutcome(outcome=o or "unknown", count=c) for o, c in outcome_query.all()
    ]

    # Inbound vs outbound
    dir_query = db.query(Call.direction, func.count(Call.id)).group_by(Call.direction)
    if business_id:
        dir_query = dir_query.filter(Call.business_id == business_id)
    inbound_vs_outbound = [
        CallOutcome(outcome=d, count=c) for d, c in dir_query.all()
    ]

    # Lead funnel
    funnel_query = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    if business_id:
        funnel_query = funnel_query.filter(Lead.business_id == business_id)
    lead_funnel = [
        LeadFunnelItem(stage=s or "unknown", count=c) for s, c in funnel_query.all()
    ]

    return DashboardChartData(
        calls_over_time=calls_over_time,
        call_outcomes=call_outcomes,
        inbound_vs_outbound=inbound_vs_outbound,
        lead_funnel=lead_funnel,
    )


def get_recent_activity(
    db: Session, business_id: Optional[int] = None, limit: int = 15
) -> list[ActivityItem]:
    """Get recent activity items."""
    query = db.query(Activity).order_by(desc(Activity.created_at)).limit(limit)
    if business_id:
        query = query.filter(Activity.business_id == business_id)

    items = []
    for a in query.all():
        items.append(
            ActivityItem(
                id=a.id,
                type=a.type,
                description=a.description,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                created_at=a.created_at.isoformat() if a.created_at else None,
            )
        )
    return items


def get_recent_calls(
    db: Session, business_id: Optional[int] = None, limit: int = 10
) -> list[dict]:
    """Get recent calls with lead info."""
    query = db.query(Call).order_by(desc(Call.created_at)).limit(limit)
    if business_id:
        query = query.filter(Call.business_id == business_id)

    results = []
    for call in query.all():
        lead_name = ""
        lead_phone = ""
        if call.lead_id:
            lead = db.query(Lead).filter(Lead.id == call.lead_id).first()
            if lead:
                lead_name = f"{lead.first_name} {lead.last_name or ''}".strip()
                lead_phone = lead.phone or ""

        results.append({
            "id": call.id,
            "lead_name": lead_name,
            "lead_phone": lead_phone,
            "direction": call.direction,
            "duration_seconds": call.duration_seconds,
            "outcome": call.outcome or "pending",
            "qualification_score": call.qualification_score,
            "appointment_booked": call.appointment_booked,
            "status": call.status,
            "created_at": call.created_at.isoformat() if call.created_at else None,
        })
    return results


def get_hot_leads(
    db: Session, business_id: Optional[int] = None, limit: int = 10
) -> list[dict]:
    """Get hot leads."""
    query = (
        db.query(Lead)
        .filter(Lead.temperature == "hot")
        .order_by(desc(Lead.qualification_score))
        .limit(limit)
    )
    if business_id:
        query = query.filter(Lead.business_id == business_id)

    return [
        {
            "id": l.id,
            "name": f"{l.first_name} {l.last_name or ''}".strip(),
            "phone": l.phone or "",
            "email": l.email or "",
            "score": l.qualification_score,
            "temperature": l.temperature,
            "status": l.status,
            "updated_at": l.updated_at.isoformat() if l.updated_at else None,
        }
        for l in query.all()
    ]


def get_upcoming_appointments(
    db: Session, business_id: Optional[int] = None, limit: int = 10
) -> list[dict]:
    """Get upcoming appointments."""
    now = datetime.now(timezone.utc)
    query = (
        db.query(Appointment)
        .filter(Appointment.start_time >= now)
        .filter(Appointment.status.in_(["scheduled", "confirmed"]))
        .order_by(Appointment.start_time)
        .limit(limit)
    )
    if business_id:
        query = query.filter(Appointment.business_id == business_id)

    return [
        {
            "id": a.id,
            "title": a.title,
            "customer_name": a.customer_name or "",
            "start_time": a.start_time.isoformat() if a.start_time else None,
            "end_time": a.end_time.isoformat() if a.end_time else None,
            "status": a.status,
        }
        for a in query.all()
    ]


def get_full_dashboard(
    db: Session, business_id: Optional[int] = None
) -> DashboardResponse:
    """Get complete dashboard data."""
    return DashboardResponse(
        overview=get_overview(db, business_id),
        charts=get_charts(db, business_id),
        recent_activity=get_recent_activity(db, business_id),
        recent_calls=get_recent_calls(db, business_id),
        hot_leads=get_hot_leads(db, business_id),
        upcoming_appointments=get_upcoming_appointments(db, business_id),
    )
