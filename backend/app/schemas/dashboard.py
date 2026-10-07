"""Dashboard Pydantic schemas."""

from typing import Any, Optional

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    total_calls: int = 0
    answered_calls: int = 0
    qualified_leads: int = 0
    appointments_booked: int = 0
    conversion_rate: float = 0.0
    avg_call_duration: float = 0.0
    total_leads: int = 0
    hot_leads: int = 0


class CallsOverTime(BaseModel):
    date: str
    count: int
    direction: str = "all"


class CallOutcome(BaseModel):
    outcome: str
    count: int


class LeadFunnelItem(BaseModel):
    stage: str
    count: int


class DashboardChartData(BaseModel):
    calls_over_time: list[CallsOverTime] = []
    call_outcomes: list[CallOutcome] = []
    inbound_vs_outbound: list[CallOutcome] = []
    lead_funnel: list[LeadFunnelItem] = []


class ActivityItem(BaseModel):
    id: int
    type: str
    description: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    created_at: Optional[str] = None


class DashboardResponse(BaseModel):
    overview: DashboardOverview
    charts: DashboardChartData
    recent_activity: list[ActivityItem] = []
    recent_calls: list[dict[str, Any]] = []
    hot_leads: list[dict[str, Any]] = []
    upcoming_appointments: list[dict[str, Any]] = []
