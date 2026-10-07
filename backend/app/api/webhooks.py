"""Webhook endpoints for Retell AI and Vapi AI."""

import json
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.logging import log
from app.database.database import get_db
from app.integrations.retell import RetellProvider
from app.api.websocket import broadcast
from app.integrations.vapi import VapiProvider
from app.models.call import Call
from app.models.lead import Lead
from app.schemas.appointment import RetellBookAppointment
from app.schemas.call import CallCreate, CallUpdate
from app.schemas.lead import LeadCreate
from app.services import call_service, lead_service
from app.services import appointment_service
from app.services.summary_service import generate_summary
from app.services.followup_service import create_followup

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


def _ensure_business(db: Session) -> int:
    """Return the ID of the default business, creating one if needed."""
    from app.models.business import Business

    biz = db.query(Business).first()
    if biz:
        return biz.id
    biz = Business(name="Default Business", industry="General")
    db.add(biz)
    db.flush()
    return biz.id


def _normalize_phone(phone: str) -> str:
    """Strip everything except digits for reliable phone comparison."""
    if not phone:
        return ""
    import re
    return re.sub(r'[^0-9]', '', phone)


# Retell custom-function arguments can arrive under many different keys
# depending on how the function is configured in the Retell dashboard.
# Map all common spellings onto our canonical field names.
_BOOK_ALIASES = {
    "customer_name": (
        "customer_name", "customerName", "customername", "name", "full_name",
        "fullName", "fullname", "caller_name", "callerName", "contact_name",
        "contactName",
    ),
    "customer_phone": (
        "customer_phone", "customerPhone", "customerphone", "phone",
        "phone_number", "phoneNumber", "phonenumber", "caller_number",
        "callerNumber", "mobile", "mobile_number", "mobileNumber",
        "contact_number", "contactNumber", "number",
    ),
    "customer_email": (
        "customer_email", "customerEmail", "email", "email_address", "emailAddress",
    ),
    "title": (
        "title", "service", "reason", "purpose", "subject",
        "appointment_type", "appointmentType", "type",
    ),
    "notes": (
        "notes", "note", "address", "comments", "comment",
        "description", "details",
    ),
    "lead_id": ("lead_id", "leadId"),
    "call_id": ("call_id", "callId"),
    "business_id": ("business_id", "businessId"),
}


# Containers that may wrap the custom-function arguments.
_ARGS_CONTAINER_KEYS = (
    "args", "arguments", "parameters", "params", "input",
    "payload", "function_args", "functionArguments", "tool_args",
)


def _flat_view(d: dict) -> dict:
    """Flatten one level of nested dicts so aliases are found regardless
    of whether Retell nests args like ``{"customer": {"name": ...}}``."""
    flat: dict = {}
    for k, v in d.items():
        flat[k] = v
        if isinstance(v, dict):
            for k2, v2 in v.items():
                flat.setdefault(k2, v2)
    return flat


def _pick(args: dict, key: str):
    """Return the first non-empty value for any known alias of *key*."""
    for alias in _BOOK_ALIASES[key]:
        if alias in args:
            val = args[alias]
            if val is not None and val != "":
                return val
    return None


def _fuzzy(args: dict, includes, excludes=()):
    """Last-resort match: first non-empty value whose key contains any of
    *includes* and none of *excludes* (case-insensitive)."""
    for k, v in args.items():
        kl = str(k).lower()
        if any(s in kl for s in includes) and not any(x in kl for x in excludes):
            if v not in (None, "", {}, []):
                return v
    return None


def _to_int(val):
    """Best-effort int coercion; returns None when not numeric."""
    if val is None or val == "":
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _extract_start_time(args: dict) -> str:
    """Resolve a start time from either a single ISO field or a
    separate date + time pair."""
    for key in (
        "start_time", "startTime", "starttime", "datetime", "date_time",
        "dateTime", "appointment_datetime", "appointmentDateTime",
        "appointment_time", "appointmentTime", "when", "start",
    ):
        val = args.get(key)
        if val:
            return str(val)
    # Fuzzy: any key mentioning date/datetime/start/appointment
    fuzzy = _fuzzy(
        args,
        includes=("datetime", "date_time", "start", "appointment", "when"),
        excludes=("end",),
    )
    if fuzzy:
        return str(fuzzy)
    date_val = (
        args.get("date") or args.get("appointment_date")
        or args.get("appointmentDate") or args.get("day")
    )
    time_val = args.get("time") or args.get("slot") or args.get("hour")
    if date_val and time_val:
        return f"{date_val}T{time_val}"
    return str(date_val or "")


def _extract_book_args(payload: dict):
    """Return ``(args, call_ctx)`` from either a flat arguments body or
    the standard Retell custom-function envelope
    ``{"name": ..., "args": {...}, "call": {...}}``.

    Retell sends the ``call`` object (which can be enormous, including the
    transcript) as a sibling of the arguments, so we look inside every
    known args container before falling back to the flat body.
    """
    if not isinstance(payload, dict):
        return {}, {}
    call_ctx = payload.get("call") if isinstance(payload.get("call"), dict) else {}
    for key in _ARGS_CONTAINER_KEYS:
        inner = payload.get(key)
        if isinstance(inner, dict) and inner:
            return inner, call_ctx
    # Flat body: everything except the call context and envelope metadata
    meta = {"call", "name", "event", "call_id"}
    return {k: v for k, v in payload.items() if k not in meta}, call_ctx


def _build_book_model(args: dict) -> RetellBookAppointment:
    """Map Retell's (possibly renamed) function arguments onto our schema."""
    flat = _flat_view(args)

    customer_name = _pick(flat, "customer_name")
    if not customer_name:
        customer_name = _fuzzy(
            flat, includes=("name",),
            excludes=("agent", "business", "function", "tool", "file"),
        )

    customer_phone = _pick(flat, "customer_phone")
    if not customer_phone:
        customer_phone = _fuzzy(
            flat, includes=("phone", "mobile", "number", "tel"),
            excludes=("agent", "business"),
        )

    title = _pick(flat, "title")
    notes = _pick(flat, "notes")

    return RetellBookAppointment(
        customer_name=str(customer_name or ""),
        customer_phone=str(customer_phone or ""),
        start_time=_extract_start_time(flat),
        end_time=str(flat.get("end_time") or flat.get("endTime") or "") or None,
        customer_email=_pick(flat, "customer_email"),
        title=str(title or ""),
        notes=notes,
        lead_id=_to_int(_pick(flat, "lead_id")),
        call_id=_to_int(_pick(flat, "call_id")),
        business_id=_to_int(_pick(flat, "business_id")),
    )


# ── Transcript fallback ───────────────────────────────────────────────
# When a Retell custom function is misconfigured with no parameters, the
# agent still collects the details verbally but the function fires with an
# empty ``args`` object.  These helpers recover the booking details from
# the call transcript so the record still reaches the dashboard.
_NUM_WORDS = {
    "zero": "0", "oh": "0", "o": "0", "one": "1", "two": "2",
    "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9",
}
_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}


def _words_to_digits(segment: str) -> str:
    """Convert a spoken number-word segment (and any literal digits) into a
    digit string, e.g. \"zero three one eight\" -> \"0318\"."""
    out = []
    for tok in re.findall(r"[a-z]+|\d+", (segment or "").lower()):
        if tok.isdigit():
            out.append(tok)
        elif tok in _NUM_WORDS:
            out.append(_NUM_WORDS[tok])
    return "".join(out)


def _parse_datetime_from_text(text: str) -> str:
    """Extract an ISO-8601 datetime from natural language, e.g.
    \"October 8th, 2026 at 10 AM\" -> \"2026-10-08T10:00:00\"."""
    month_re = "(" + "|".join(_MONTHS.keys()) + ")"
    pattern = (
        month_re
        + r"\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})?"
        + r"\s*(?:at\s+)?(\d{1,2})(?!\d)(?::(\d{2}))?\s*(am|pm)?"
    )
    m = re.search(pattern, text or "", re.IGNORECASE)
    if not m:
        return ""
    month = _MONTHS[m.group(1).lower()]
    day = int(m.group(2))
    year = int(m.group(3)) if m.group(3) else datetime.now(timezone.utc).year
    hour = int(m.group(4))
    minute = int(m.group(5) or 0)
    ampm = (m.group(6) or "").lower()
    if ampm == "pm" and hour < 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"


def _parse_booking_from_transcript(transcript: str) -> dict:
    """Best-effort recovery of booking details from a Retell transcript."""
    if not transcript:
        return {}
    text = transcript.replace("\r", " ")
    result: dict = {}
    turns = [
        (match.group(1).lower(), match.group(2).strip())
        for match in re.finditer(
            r"(?ms)^(Agent|User):\s*(.*?)(?=^(?:Agent|User):|\Z)", text
        )
    ]

    m = re.search(r"my name is ([^\.\n,]+)", text, re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        # Drop trailing connector words like "and"
        name = re.split(r"\s+and\s+", name, flags=re.IGNORECASE)[0].strip()
        if name:
            result["customer_name"] = name

    m = re.search(r"phone number is ([^,\.\n]+)", text, re.IGNORECASE)
    if m:
        digits = _words_to_digits(m.group(1))
        if len(digits) >= 7:
            result["customer_phone"] = digits
    if not result.get("customer_phone"):
        phone_prompts = [
            i for i, (speaker, content) in enumerate(turns)
            if speaker == "agent" and re.search(r"\b(phone|mobile|number)\b", content, re.I)
        ]
        for prompt_index in reversed(phone_prompts):
            answer = []
            for speaker, content in turns[prompt_index + 1:]:
                if speaker == "agent":
                    if re.search(r"\b(address|location|when|date|time|schedule)\b", content, re.I):
                        break
                    continue
                answer.append(content)
            digits = _words_to_digits(" ".join(answer))
            if len(digits) >= 7:
                result["customer_phone"] = digits
                break

    m = re.search(r"address is ([^\.\n]+)", text, re.IGNORECASE)
    if m:
        result["notes"] = m.group(1).strip().rstrip(",")
    if not result.get("notes"):
        address_prompts = [
            i for i, (speaker, content) in enumerate(turns)
            if speaker == "agent" and re.search(r"\b(address|location)\b", content, re.I)
        ]
        for prompt_index in reversed(address_prompts):
            answer = []
            for speaker, content in turns[prompt_index + 1:]:
                if speaker == "agent":
                    if re.search(r"\b(when|date|time|schedule)\b", content, re.I):
                        break
                    continue
                answer.append(content)
            address = re.sub(r"\s+", " ", " ".join(answer)).strip()
            if address:
                result["notes"] = address
                break

    dt = _parse_datetime_from_text(text)
    if dt:
        result["start_time"] = dt

    return result


def _find_or_create_lead(db: Session, data: dict, business_id: int = None) -> Lead:
    """Find existing lead by phone or create a new one."""
    if business_id is None:
        business_id = _ensure_business(db)

    phone = data.get("phone") or data.get("caller_number")
    email = data.get("email")

    if phone:
        # Exact match
        lead = db.query(Lead).filter(Lead.phone == phone).first()
        if lead:
            return lead
        # Digits-only fuzzy match
        phone_digits = _normalize_phone(phone)
        if len(phone_digits) >= 7:
            for ml in db.query(Lead).filter(Lead.phone.isnot(None)).all():
                ml_digits = _normalize_phone(ml.phone)
                if not ml_digits:
                    continue
                shorter = phone_digits if len(phone_digits) <= len(ml_digits) else ml_digits
                longer = ml_digits if len(ml_digits) >= len(phone_digits) else phone_digits
                if shorter in longer or longer.endswith(shorter[-8:]):
                    return ml

    if email:
        lead = db.query(Lead).filter(Lead.email == email).first()
        if lead:
            return lead

    # Create new lead
    name_parts = (data.get("caller_name") or "").split(" ", 1)
    lead_data = LeadCreate(
        first_name=name_parts[0] if name_parts else "Unknown",
        last_name=name_parts[1] if len(name_parts) > 1 else None,
        phone=phone,
        email=email,
        business_id=business_id,
    )
    return lead_service.create_lead(db, lead_data, business_id=business_id)


async def _process_call_event(db: Session, normalized: dict, business_id: int = 1) -> dict:
    """Process a normalized webhook event into call/lead/activity records."""
    external_id = normalized.get("external_id")

    # Idempotency check — update existing call if one already exists for this external_id
    if external_id:
        existing = call_service.get_call_by_external_id(db, external_id)
        if existing:
            update_fields = {}
            for key in ("status", "outcome", "transcript", "summary",
                        "recording_url", "sentiment"):
                val = normalized.get(key)
                if val is not None:
                    update_fields[key] = val
            # Only include duration_seconds when the event actually provides it (> 0)
            dur = normalized.get("duration_seconds", 0)
            if dur > 0:
                update_fields["duration_seconds"] = dur
            if update_fields:
                call_service.update_call(db, existing.id, CallUpdate(**update_fields))

            # Generate summary from transcript if available and not already set
            if normalized.get("transcript") and not existing.summary and not normalized.get("summary"):
                summary = await generate_summary(normalized["transcript"])
                call_service.update_call(db, existing.id, CallUpdate(
                    summary=json.dumps(summary),
                    qualification_score=summary.get("qualification_score", 0),
                ))

            # Mark appointment_booked flag on the call record
            if normalized.get("outcome") == "appointment_booked":
                call_service.update_call(db, existing.id, CallUpdate(appointment_booked="1"))

            # Update lead status based on outcome
            if normalized.get("outcome") and existing.lead_id:
                lead = db.query(Lead).filter(Lead.id == existing.lead_id).first()
                if lead:
                    if normalized["outcome"] == "qualified":
                        lead.status = "qualified"
                        lead.temperature = "hot"
                    elif normalized["outcome"] == "appointment_booked":
                        lead.status = "appointment_booked"
                    elif normalized["outcome"] == "not_interested":
                        lead.status = "lost"
            db.commit()

            return {"status": "updated", "call_id": existing.id}

    # Find or create lead
    lead = _find_or_create_lead(db, {
        "phone": normalized.get("phone"),
        "email": normalized.get("email"),
        "caller_name": normalized.get("caller_name"),
    }, business_id=business_id)

    # Create call
    call = call_service.create_call(
        db,
        CallCreate(
            direction=normalized.get("direction", "inbound"),
            business_id=business_id,
            lead_id=lead.id,
            external_call_id=external_id,
        ),
        business_id=business_id,
    )

    # Update call with event data
    update_fields = {}
    if normalized.get("status"):
        update_fields["status"] = normalized["status"]
    if normalized.get("outcome"):
        update_fields["outcome"] = normalized["outcome"]
    if normalized.get("transcript"):
        update_fields["transcript"] = normalized["transcript"]
    if normalized.get("summary"):
        update_fields["summary"] = normalized["summary"]
    if normalized.get("duration_seconds"):
        update_fields["duration_seconds"] = normalized["duration_seconds"]
    if normalized.get("recording_url"):
        update_fields["recording_url"] = normalized["recording_url"]
    if normalized.get("sentiment"):
        update_fields["sentiment"] = normalized["sentiment"]

    if update_fields:
        call_service.update_call(db, call.id, CallUpdate(**update_fields))

    # Generate summary if transcript available
    if normalized.get("transcript") and not normalized.get("summary"):
        summary = await generate_summary(normalized["transcript"])
        call_service.update_call(db, call.id, CallUpdate(
            summary=json.dumps(summary),
            qualification_score=summary.get("qualification_score", 0),
        ))

    # Mark appointment_booked flag on the call record
    if normalized.get("outcome") == "appointment_booked":
        call_service.update_call(db, call.id, CallUpdate(appointment_booked="1"))

    # Update lead status based on outcome
    if normalized.get("outcome") == "qualified":
        lead.status = "qualified"
        lead.temperature = "hot"
    elif normalized.get("outcome") == "appointment_booked":
        lead.status = "appointment_booked"
    elif normalized.get("outcome") == "not_interested":
        lead.status = "lost"
    db.commit()

    return {"status": "processed", "call_id": call.id, "lead_id": lead.id}


async def _process_book_appointment(db: Session, data, call_ctx: dict = None) -> dict:
    """Core book-appointment logic shared by the dedicated endpoint and
    the general webhook's custom-function handler.

    *data* must be a ``RetellBookAppointment`` instance.
    *call_ctx* is the optional ``call`` object from the Retell custom-function
    payload (contains transcript, call_id, etc.).
    """
    from datetime import datetime as dt, timedelta
    from app.schemas.appointment import AppointmentCreate
    from app.schemas.call import CallCreate as _CallCreate, CallUpdate as _CallUpdate
    from app.schemas.lead import LeadCreate as _LeadCreate
    from app.utils.date_utils import normalize_appointment_date

    # --- Parse & normalize datetime strings -------------------------------
    start_time = normalize_appointment_date(data.start_time)
    end_time = None
    if data.end_time:
        end_time = normalize_appointment_date(data.end_time)

    # --- Ensure a business exists ---------------------------------------
    business_id = data.business_id or _ensure_business(db)

    # --- Validate referenced entities (when explicitly provided) ---------
    if data.lead_id is not None:
        existing_lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
        if not existing_lead:
            raise ValueError(f"Lead {data.lead_id} not found")

    if data.call_id is not None:
        existing_call_check = db.query(Call).filter(Call.id == data.call_id).first()
        if not existing_call_check:
            raise ValueError(f"Call {data.call_id} not found")

    # --- Resolve or create Lead ------------------------------------------
    if not data.lead_id:
        phone = data.customer_phone
        lead = None
        if phone:
            # 1) Exact match on full phone string
            lead = db.query(Lead).filter(Lead.phone == phone).order_by(Lead.id.desc()).first()
            # 2) Digits-only match (strips +, spaces, dashes, parens, country code)
            if not lead:
                phone_digits = _normalize_phone(phone)
                if len(phone_digits) >= 7:
                    for ml in db.query(Lead).filter(Lead.phone.isnot(None)).all():
                        ml_digits = _normalize_phone(ml.phone)
                        if not ml_digits:
                            continue
                        # Match if the shorter number is contained in the longer one
                        shorter = phone_digits if len(phone_digits) <= len(ml_digits) else ml_digits
                        longer = ml_digits if len(ml_digits) >= len(phone_digits) else phone_digits
                        if shorter in longer or longer.endswith(shorter[-8:]):
                            lead = ml
                            break
        if not lead:
            name_parts = (data.customer_name or "").split(" ", 1)
            lead = lead_service.create_lead(
                db,
                _LeadCreate(
                    first_name=name_parts[0] if name_parts else "Unknown",
                    last_name=name_parts[1] if len(name_parts) > 1 else None,
                    phone=phone,
                    email=data.customer_email,
                    source="inbound_call",
                    business_id=business_id,
                    notes=f"Created from Retell book-appointment for: {data.title or data.customer_name}",
                ),
                business_id=business_id,
            )
        lead.status = "appointment_booked"
        lead.temperature = "hot"
        db.commit()
        data.lead_id = lead.id
    else:
        lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
        if lead:
            lead.status = "appointment_booked"
            lead.temperature = "hot"
            db.commit()

    # --- Resolve or create Call ------------------------------------------
    if not data.call_id:
        recent_cutoff = dt.now(timezone.utc) - timedelta(minutes=10)
        existing_call = None

        # 1) Try to find by external_call_id from the Retell call context
        #    (the call_started webhook already created the call record)
        retell_call_id = call_ctx.get("call_id") if call_ctx else None
        if retell_call_id:
            existing_call = (
                db.query(Call)
                .filter(Call.external_call_id == retell_call_id)
                .first()
            )

        # 2) Fall back to lead_id + time-based lookup
        if not existing_call:
            existing_call = (
                db.query(Call)
                .filter(Call.lead_id == lead.id)
                .filter(Call.created_at >= recent_cutoff)
                .order_by(Call.created_at.desc())
                .first()
            )

        # 3) Fuzzy phone match fallback — search all leads for a recent call
        if not existing_call and data.customer_phone:
            phone_digits = _normalize_phone(data.customer_phone)
            if len(phone_digits) >= 7:
                for ml in db.query(Lead).filter(Lead.phone.isnot(None)).all():
                    ml_digits = _normalize_phone(ml.phone)
                    if not ml_digits:
                        continue
                    shorter = phone_digits if len(phone_digits) <= len(ml_digits) else ml_digits
                    longer = ml_digits if len(ml_digits) >= len(phone_digits) else phone_digits
                    if shorter in longer or longer.endswith(shorter[-8:]):
                        existing_call = (
                            db.query(Call)
                            .filter(Call.lead_id == ml.id)
                            .filter(Call.created_at >= recent_cutoff)
                            .order_by(Call.created_at.desc())
                            .first()
                        )
                        if existing_call:
                            lead = ml
                            data.lead_id = ml.id
                            break

        # 4) Last resort: find the most recent active call across ALL leads
        #    within the time window. This catches cases where phone formats
        #    differ enough that all matching above fails.
        if not existing_call:
            most_recent_call = (
                db.query(Call)
                .filter(Call.created_at >= recent_cutoff)
                .order_by(Call.created_at.desc())
                .first()
            )
            if most_recent_call:
                existing_call = most_recent_call
                # Re-link the lead to this call
                if existing_call.lead_id and existing_call.lead_id != lead.id:
                    # The original call has a different lead — use that lead instead
                    original_lead = db.query(Lead).filter(Lead.id == existing_call.lead_id).first()
                    if original_lead:
                        lead = original_lead
                        data.lead_id = original_lead.id
                        # Update the original lead status too
                        original_lead.status = "appointment_booked"
                        original_lead.temperature = "hot"
                        db.commit()
                elif not existing_call.lead_id:
                    existing_call.lead_id = lead.id

        if existing_call:
            call = existing_call
            # Keep the matched Retell call linked to the lead resolved for this booking.
            if call.lead_id != lead.id:
                call.lead_id = lead.id
            call_service.update_call(db, call.id, _CallUpdate(
                status="completed",
                outcome="appointment_booked",
                appointment_booked="1",
            ))
            # Back-fill transcript from call context if available
            if call_ctx and call_ctx.get("transcript") and not call.transcript:
                call_service.update_call(db, call.id, _CallUpdate(
                    transcript=call_ctx["transcript"],
                ))
            # Back-fill external_call_id if available
            if call_ctx and call_ctx.get("call_id") and not call.external_call_id:
                call_service.update_call(db, call.id, _CallUpdate(
                    external_call_id=call_ctx["call_id"],
                ))
        else:
            call = call_service.create_call(
                db,
                _CallCreate(
                    direction="inbound",
                    lead_id=lead.id,
                    business_id=business_id,
                ),
                business_id=business_id,
            )
            call_update = _CallUpdate(
                status="completed",
                outcome="appointment_booked",
                appointment_booked="1",
            )
            # Back-fill transcript & external_call_id from call context
            if call_ctx:
                if call_ctx.get("transcript"):
                    call_update.transcript = call_ctx["transcript"]
                if call_ctx.get("call_id"):
                    call_update.external_call_id = call_ctx["call_id"]
                if call_ctx.get("start_timestamp") and call_ctx.get("end_timestamp"):
                    dur = (call_ctx["end_timestamp"] - call_ctx["start_timestamp"]) // 1000
                    if dur > 0:
                        call_update.duration_seconds = dur
            call_service.update_call(db, call.id, call_update)
        data.call_id = call.id
    else:
        call = db.query(Call).filter(Call.id == data.call_id).first()
        if call:
            call.appointment_booked = "1"
            if call.outcome is None:
                call.outcome = "appointment_booked"
            db.commit()

    # --- Create the Appointment ------------------------------------------
    appt_data = AppointmentCreate(
        title=data.title or f"Appointment with {data.customer_name}",
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        customer_email=data.customer_email,
        start_time=start_time,
        end_time=end_time,
        notes=data.notes,
        business_id=business_id,
        lead_id=data.lead_id,
        call_id=data.call_id,
    )

    appointment = appointment_service.create_appointment(db, appt_data)

    log.info(
        "Retell book-appointment: created appointment %s (lead=%s, call=%s) for %s",
        appointment.id, data.lead_id, data.call_id, data.customer_name,
    )

    return {
        "status": "ok",
        "appointment_id": appointment.id,
        "lead_id": data.lead_id,
        "call_id": data.call_id,
        "title": appointment.title,
        "start_time": appointment.start_time.isoformat(),
        "message": f"Appointment booked for {data.customer_name} at {appointment.start_time}.",
    }


def _is_retell_custom_function(payload: dict) -> bool:
    """Detect if a Retell payload is a custom function call.

    Retell custom function payloads have a ``name`` field (the function name)
    and an ``args`` dict — *or* they arrive in "Payload: args only" mode
    where the body is the flat arguments object with no wrapper.

    Lifecycle webhook payloads always have an ``event`` field and a ``call``
    object but no ``name`` / ``args`` fields.
    """
    # Standard custom-function payload: {"name": ..., "args": ..., "call": ...}
    if "name" in payload and (
        "args" in payload or "arguments" in payload or "parameters" in payload
    ):
        return True
    # Any args container present → custom function
    if any(k in payload for k in _ARGS_CONTAINER_KEYS):
        return True
    # "Payload: args only" mode / no lifecycle ``event`` → custom function
    if "event" not in payload:
        return True
    return False


async def _handle_custom_function(
    payload: dict, db: Session, request: Request,
) -> dict:
    """Route a Retell custom-function payload to the right handler."""
    func_name = payload.get("name", "")
    normalized_func_name = re.sub(r"[^a-z0-9]", "", func_name.lower())

    # --- book_appointment ------------------------------------------------
    if normalized_func_name == "bookappointment" or (
        func_name == "" and "event" not in payload
    ):
        # Extract args: standard mode has ``args`` dict; args-only mode
        # is the payload itself.
        args, call_ctx = _extract_book_args(payload)

        # Build the same body the dedicated /book-appointment endpoint expects
        book_data = _build_book_model(args)

        log.info(
            "Retell custom function 'book_appointment' received via general webhook — "
            "routing to book-appointment handler"
        )
        result = await _process_book_appointment(db, book_data, call_ctx)

        try:
            await broadcast({
                "type": "call_update",
                "event": "book_appointment",
                "call_id": result.get("call_id"),
                "lead_id": result.get("lead_id"),
            })
        except Exception as exc:
            log.warning("WebSocket broadcast failed (non-fatal): %s", exc)

        return result

    # --- Unknown custom function — fall through to lifecycle handling ------
    provider = RetellProvider()
    normalized = provider.process_webhook(payload)
    return await _process_call_event(db, normalized)


@router.post("/retell", summary="Retell AI webhook receiver")
async def retell_webhook(request: Request, db: Session = Depends(get_db)):
    """Process incoming Retell AI webhook events.

    Handles two kinds of payloads from Retell:

    1. **Lifecycle webhooks** – ``call_started``, ``call_ended``,
       ``call_analyzed``, etc.  Identified by having an ``event`` field.

    2. **Custom function calls** – e.g. ``book_appointment``.  Identified by
       having a ``name`` field (standard mode) or by lacking both ``event``
       and ``call`` keys ("Payload: args only" mode).
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # --- Route custom-function payloads to the right handler --------------
    if _is_retell_custom_function(payload):
        log.info(
            "Retell custom function call received: %s",
            payload.get("name", "(args-only)"),
        )
        result = await _handle_custom_function(payload, db, request)
        log.info("Retell custom function processed: %s", result)
        return {"status": "ok", "result": result}

    # --- Standard lifecycle webhook ---------------------------------------
    log.info("Retell webhook received: %s", payload.get("event", "unknown"))

    provider = RetellProvider()
    normalized = provider.process_webhook(payload)

    result = await _process_call_event(db, normalized)

    log.info("Retell webhook processed: %s", result)

    # Broadcast real-time update to connected dashboard clients
    try:
        await broadcast({
            "type": "call_update",
            "event": payload.get("event", "unknown"),
            "call_id": result.get("call_id"),
            "lead_id": result.get("lead_id"),
        })
    except Exception as exc:
        log.warning("WebSocket broadcast failed (non-fatal): %s", exc)

    return {"status": "ok", "result": result}


@router.post("/vapi", summary="Vapi AI webhook receiver")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    """Process incoming Vapi AI webhook events."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    log.info("Vapi webhook received: %s", payload.get("message", {}).get("type", "unknown"))

    provider = VapiProvider()
    normalized = provider.process_webhook(payload)

    result = await _process_call_event(db, normalized)

    log.info("Vapi webhook processed: %s", result)
    return {"status": "ok", "result": result}


# ──────────────────────────────────────────────────────────────────────
# Retell AI Custom Function — Book Appointment
# ──────────────────────────────────────────────────────────────────────

@router.post("/retell/book-appointment", summary="Retell AI: book an appointment")
async def retell_book_appointment(
    request: Request,
    db: Session = Depends(get_db),
):
    """Public endpoint for Retell AI Custom Functions to book an appointment.

    No JWT required — Retell cannot carry bearer tokens in function calls.

    Accepts either payload shape Retell may send:

    * **Envelope** – ``{"name": "book_appointment", "args": {...}, "call": {...}}``
    * **Flat args** – ``{"customer_name": ..., "customer_phone": ..., ...}``

    Field names are also normalized, so functions configured with ``name`` /
    ``phone`` / ``date`` (or other aliases) still work.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    args, call_ctx = _extract_book_args(payload)
    log.info(
        "Retell book-appointment payload keys=%s call_keys=%s args=%s",
        list(payload.keys()),
        list(call_ctx.keys()),
        {k: v for k, v in args.items() if not isinstance(v, (dict, list))},
    )
    data = _build_book_model(args)

    # Safety net: a Retell function configured with no parameters fires with
    # an empty ``args`` object. Recover the details from the call transcript
    # so the booking still reaches the dashboard.
    if not (data.customer_name and data.customer_phone and data.start_time):
        derived = _parse_booking_from_transcript(
            call_ctx.get("transcript") or args.get("transcript") or ""
        )
        log.info("Retell book-appointment transcript fallback derived: %s", derived)
        if derived:
            if not data.customer_name and derived.get("customer_name"):
                data.customer_name = derived["customer_name"]
            if not data.customer_phone and derived.get("customer_phone"):
                data.customer_phone = derived["customer_phone"]
            if not data.start_time and derived.get("start_time"):
                data.start_time = derived["start_time"]
            if not data.notes and derived.get("notes"):
                data.notes = derived["notes"]
            if not data.title:
                data.title = "Roof Inspection"

    missing = [
        name for name, val in (
            ("customer_name", data.customer_name),
            ("customer_phone", data.customer_phone),
            ("start_time", data.start_time),
        ) if not val
    ]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {', '.join(missing)}",
        )

    try:
        result = await _process_book_appointment(db, data, call_ctx)
        try:
            await broadcast({
                "type": "call_update",
                "event": "book_appointment",
                "call_id": result.get("call_id"),
                "lead_id": result.get("lead_id"),
            })
        except Exception as exc:
            log.warning("WebSocket broadcast failed (non-fatal): %s", exc)
        return result
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=422, detail=str(exc))
