"""Input validation utilities."""

VALID_LEAD_STATUSES = [
    "new", "contacted", "qualified", "unqualified",
    "appointment_booked", "follow_up", "converted", "lost",
]

VALID_LEAD_TEMPERATURES = ["cold", "warm", "hot"]

VALID_CALL_DIRECTIONS = ["inbound", "outbound"]

VALID_CALL_STATUSES = [
    "initiated", "ringing", "answered", "completed", "failed", "missed",
]

VALID_CALL_OUTCOMES = [
    "qualified", "unqualified", "appointment_booked", "callback_requested",
    "transferred", "no_answer", "voicemail", "not_interested",
    "wrong_number", "information_request", "other",
]

VALID_APPOINTMENT_STATUSES = [
    "scheduled", "confirmed", "completed", "cancelled", "rescheduled", "no_show",
]

VALID_CAMPAIGN_STATUSES = ["draft", "active", "paused", "completed"]

VALID_FOLLOWUP_TYPES = ["sms", "email", "call", "manual"]

VALID_FOLLOWUP_STATUSES = ["pending", "sent", "completed", "failed"]


def validate_lead_status(status: str) -> bool:
    return status in VALID_LEAD_STATUSES


def validate_lead_temperature(temp: str) -> bool:
    return temp in VALID_LEAD_TEMPERATURES
