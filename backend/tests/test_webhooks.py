"""Webhook processing tests."""


def test_retell_webhook_call_started(client):
    payload = {
        "event": "call_started",
        "call": {
            "call_id": "test_retell_001",
            "direction": "inbound",
            "caller_number": "+15559999999",
        },
    }
    response = client.post("/api/webhooks/retell", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_retell_webhook_call_ended(client):
    # First send call_started to create the call
    client.post("/api/webhooks/retell", json={
        "event": "call_started",
        "call": {"call_id": "test_retell_002", "direction": "inbound", "caller_number": "+15558888888"},
    })
    # Then send call_ended
    payload = {
        "event": "call_ended",
        "call": {
            "call_id": "test_retell_002",
            "direction": "inbound",
            "caller_number": "+15558888888",
            "duration_ms": 60000,
        },
    }
    response = client.post("/api/webhooks/retell", json=payload)
    assert response.status_code == 200


def test_vapi_webhook(client):
    payload = {
        "message": {
            "type": "call_started",
            "call": {
                "id": "test_vapi_001",
                "direction": "outbound",
                "phone_number": "+15557777777",
            },
        },
    }
    response = client.post("/api/webhooks/vapi", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_webhook_duplicate_protection(client):
    """Sending the same webhook twice should update, not duplicate."""
    payload = {
        "event": "call_started",
        "call": {
            "call_id": "test_dupe_001",
            "direction": "inbound",
            "caller_number": "+15556666666",
        },
    }
    resp1 = client.post("/api/webhooks/retell", json=payload)
    resp2 = client.post("/api/webhooks/retell", json=payload)
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    # Both should reference the same call
    assert resp1.json()["result"]["call_id"] == resp2.json()["result"]["call_id"]


# ──────────────────────────────────────────────────────────────────────
# Retell custom-function routing tests (general webhook → book-appointment)
# ──────────────────────────────────────────────────────────────────────

def test_retell_custom_function_book_appointment_via_general_webhook(client, db):
    """When Retell's custom function hits the general webhook, it must be
    routed to the book-appointment handler and create an appointment."""
    from app.models.lead import Lead
    from app.models.call import Call
    from app.models.appointment import Appointment

    payload = {
        "name": "book_appointment",
        "args": {
            "customer_name": "John Michael",
            "customer_phone": "+15550000099",
            "start_time": "2026-09-20T14:00:00",
            "title": "Roof Inspection",
            "address": "Burger Town, Islamabad house two",
        },
        "call": {
            "call_id": "retell_call_custom_fn_test",
            "transcript": "Agent: Hello! User: I want to book.",
        },
    }
    resp = client.post("/api/webhooks/retell", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    result = data["result"]
    assert result["status"] == "ok"
    assert "appointment_id" in result
    assert result["lead_id"] is not None
    assert result["call_id"] is not None

    # The lead should have proper name and phone
    lead = db.query(Lead).filter(Lead.id == result["lead_id"]).first()
    assert lead is not None
    assert lead.first_name == "John"
    assert lead.last_name == "Michael"
    assert lead.phone == "+15550000099"
    assert lead.status == "appointment_booked"

    # The call should have the transcript and external_call_id from call context
    call = db.query(Call).filter(Call.id == result["call_id"]).first()
    assert call is not None
    assert call.transcript is not None
    assert call.external_call_id == "retell_call_custom_fn_test"
    assert call.outcome == "appointment_booked"

    # An appointment must exist
    appt = db.query(Appointment).filter(Appointment.id == result["appointment_id"]).first()
    assert appt is not None
    assert appt.customer_name == "John Michael"


def test_retell_capitalized_book_appointment_via_general_webhook(client, db):
    """Retell function names may use PascalCase on the general webhook."""
    from app.models.appointment import Appointment

    response = client.post("/api/webhooks/retell", json={
        "name": "BookAppointment",
        "args": {
            "name": "Casey Jones",
            "phone": "+15550000123",
            "date": "2027-06-18",
            "time": "10:30",
        },
        "call": {"call_id": "retell_pascalcase_test"},
    })

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["appointment_id"] is not None
    appointment = db.query(Appointment).filter(
        Appointment.id == result["appointment_id"]
    ).first()
    assert appointment is not None
    assert appointment.customer_name == "Casey Jones"


def test_retell_lifecycle_webhook_still_works(client):
    """Ensure lifecycle webhooks (call_started, call_ended) still route
    correctly and don't get confused with custom-function payloads."""
    # call_started
    resp1 = client.post("/api/webhooks/retell", json={
        "event": "call_started",
        "call": {
            "call_id": "retell_lifecycle_test_001",
            "direction": "inbound",
            "caller_number": "+15551112233",
        },
    })
    assert resp1.status_code == 200
    assert resp1.json()["result"]["status"] == "processed"

    # call_ended
    resp2 = client.post("/api/webhooks/retell", json={
        "event": "call_ended",
        "call": {
            "call_id": "retell_lifecycle_test_001",
            "direction": "inbound",
            "caller_number": "+15551112233",
            "duration_ms": 120000,
        },
    })
    assert resp2.status_code == 200


# ──────────────────────────────────────────────────────────────────────
# Retell book-appointment webhook tests
# ──────────────────────────────────────────────────────────────────────

def test_retell_book_appointment(client):
    """Public endpoint creates an appointment without JWT."""
    payload = {
        "customer_name": "Jane Doe",
        "customer_phone": "+15551234567",
        "start_time": "2026-09-15T10:00:00",
        "title": "Roof Inspection",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "appointment_id" in body
    assert body["title"] == "Roof Inspection"

def test_retell_book_appointment_creates_activity(client, db):
    """Appointment creation also logs an Activity record."""
    from app.models.activity import Activity

    payload = {
        "customer_name": "John Smith",
        "customer_phone": "+15559876543",
        "start_time": "2026-09-16T14:30:00",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    appt_id = resp.json()["appointment_id"]

    activity = db.query(Activity).filter(
        Activity.entity_type == "appointment",
        Activity.entity_id == appt_id,
    ).first()
    assert activity is not None
    assert activity.type == "appointment_booked"

def test_retell_book_appointment_accepts_retell_envelope(client, db):
    """Regression: Retell's standard custom-function envelope must book via
    the dedicated /book-appointment endpoint instead of returning 422.

    Real Retell sends ``{name, args, call}`` and the function is often
    configured with renamed args (name/phone/date/time), which the original
    strict schema rejected with 422.
    """
    from app.models.appointment import Appointment

    payload = {
        "name": "book_appointment",
        "args": {
            "name": "Passion Rufin",
            "phone": "0319648256",
            "date": "2026-10-06",
            "time": "09:00",
            "address": "Islamabad Street 4, house 2",
        },
        "call": {"call_id": "retell_env_001", "transcript": "Agent: Hi..."},
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["appointment_id"] is not None
    assert body["lead_id"] is not None
    assert body["call_id"] is not None

    appt = db.query(Appointment).filter(Appointment.id == body["appointment_id"]).first()
    assert appt is not None
    assert appt.customer_name == "Passion Rufin"
    assert appt.customer_phone == "0319648256"
    # Month/day/time from the separate date + time args were combined
    assert (appt.start_time.month, appt.start_time.day, appt.start_time.hour) == (10, 6, 9)


def test_parse_booking_from_transcript_real_call():
    """The transcript parser recovers details from a real Retell call where
    the function fired with empty args."""
    from app.api.webhooks import _parse_booking_from_transcript

    transcript = (
        "User: roof inspection. \n"
        "Agent: Hi, thanks for calling Elite Roofing! This is our AI assistant.\n"
        "User: I want to book an appointment for roof inspection. My name is Sam. "
        "My phone number is zero three one eight seven six five four three, and my "
        "address is Islamabad House twenty four Street, number three two four. \n"
        "Agent: I can help with that, Sam. When would you like to schedule the inspection?\n"
        "User: On October eight, ten year. \n"
        "Agent: Just to confirm - you'd like the inspection on October 8th, 2026 at 10 AM. "
        "Is that correct?\n"
        "User: Yes. Correct. Book an appointment. \n"
    )
    d = _parse_booking_from_transcript(transcript)
    assert d["customer_name"] == "Sam"
    assert d["customer_phone"] == "031876543"
    assert d["start_time"] == "2026-10-08T10:00:00"
    assert "Islamabad" in d["notes"]


def test_book_appointment_with_empty_args_uses_transcript(client, db):
    """Regression: Retell function misconfigured with no parameters sends
    ``args: {}``. The endpoint must recover the booking from the transcript
    instead of returning 422."""
    from app.models.appointment import Appointment

    payload = {
        "call": {
            "call_id": "retell_empty_args_001",
            "call_type": "web_call",
            "transcript": (
                "User: I want to book an appointment for roof inspection. My name is Sam. "
                "My phone number is zero three one eight seven six five four three, and my "
                "address is Islamabad House twenty four Street, number three two four. \n"
                "Agent: Just to confirm - you'd like the inspection on October 8th, 2026 "
                "at 10 AM. Is that correct?\n"
                "User: Yes. Correct. Book an appointment. \n"
            ),
        },
        "name": "BookAppointment",
        "args": {},
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "ok"
    appt = db.query(Appointment).filter(Appointment.id == body["appointment_id"]).first()
    assert appt is not None
    assert appt.customer_name == "Sam"
    assert appt.customer_phone == "031876543"
    assert (appt.start_time.month, appt.start_time.day, appt.start_time.hour) == (10, 8, 10)


def test_real_retell_empty_args_booking_reaches_dashboard(client, db, auth_headers):
    """Recover booking answers from the real Retell turn-by-turn transcript."""
    from app.models.appointment import Appointment
    from app.models.call import Call
    from app.models.lead import Lead

    external_call_id = "retell_abdullah_empty_args_001"
    placeholder_lead = Lead(first_name="Unknown")
    db.add(placeholder_lead)
    db.flush()
    existing_call = Call(
        direction="inbound",
        lead_id=placeholder_lead.id,
        external_call_id=external_call_id,
    )
    db.add(existing_call)
    db.commit()

    transcript = (
        "User: My name is Abdullah.\n"
        "Agent: What's the best phone number to reach\n"
        "User: Zero\n"
        "Agent: you at, Abdullah?\n"
        "User: three one seven eight two four eight.\n"
        "Agent: Could you repeat the full phone number, including all digits?\n"
        "User: Zero three one seven nine four eight six two one six.\n"
        "Agent: Got it. What's the address for the inspection?\n"
        "User: Lahore\n"
        "User: Street number four and three house number.\n"
        "Agent: What's the house number on Street 43?\n"
        "User: House number forty two.\n"
        "Agent: When would you like to schedule the inspection?\n"
        "User: With time I I we can easily come on seventh of October.\n"
        "Agent: What time on Wednesday, October 7th, 2026 would work for you?\n"
        "User: Anytime.\n"
        "Agent: Our inspections are available from 8 AM to 6 PM. Would 10 AM on Wednesday, October 7th, 2026 work\n"
        "User: Okay. Okay. So book at six PM.\n"
        "Agent: Just to confirm - you'd like the inspection on Wednesday, October 7th, 2026 at 6 PM. Is that correct?\n"
        "User: Please correct book an appointment.\n"
    )
    payload = {
        "name": "BookAppointment",
        "args": {},
        "call": {
            "call_id": external_call_id,
            "call_type": "web_call",
            "transcript": transcript,
        },
    }

    response = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    appointment = db.query(Appointment).filter(
        Appointment.id == body["appointment_id"]
    ).first()
    assert appointment is not None
    assert appointment.customer_name == "Abdullah"
    assert appointment.customer_phone == "03179486216"
    assert appointment.start_time.hour == 18
    assert "Lahore" in appointment.notes
    assert "House number forty two" in appointment.notes
    call = db.query(Call).filter(Call.id == appointment.call_id).first()
    assert call is not None
    assert call.lead_id == appointment.lead_id

    dashboard = client.get("/api/dashboard", headers=auth_headers)
    assert dashboard.status_code == 200
    assert any(
        item["id"] == appointment.id
        for item in dashboard.json()["upcoming_appointments"]
    )


def test_retell_book_appointment_with_lead_and_call(client, db, test_business):
    """Endpoint links appointment to existing lead and call."""
    from app.models.lead import Lead
    from app.models.call import Call

    # Create a lead
    lead = Lead(
        first_name="Alice",
        last_name="Wong",
        phone="+15550001111",
        business_id=test_business.id,
    )
    db.add(lead)
    db.flush()

    # Create a call linked to that lead
    call = Call(
        direction="inbound",
        business_id=test_business.id,
        lead_id=lead.id,
    )
    db.add(call)
    db.commit()

    payload = {
        "customer_name": "Alice Wong",
        "customer_phone": "+15550001111",
        "start_time": "2026-09-17T09:00:00",
        "lead_id": lead.id,
        "call_id": call.id,
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"

    # Verify the appointment is linked
    from app.models.appointment import Appointment
    appt = db.query(Appointment).filter(Appointment.id == body["appointment_id"]).first()
    assert appt.lead_id == lead.id
    assert appt.call_id == call.id

def test_retell_book_appointment_invalid_lead(client):
    """Returns 404 when lead_id does not exist."""
    payload = {
        "customer_name": "Nobody",
        "customer_phone": "+15550000000",
        "start_time": "2026-09-18T08:00:00",
        "lead_id": 99999,
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 404

def test_retell_book_appointment_invalid_start_time(client):
    """Returns 422 when start_time is not valid ISO 8601."""
    payload = {
        "customer_name": "Bad Date",
        "customer_phone": "+15550000000",
        "start_time": "not-a-date",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 422

def test_retell_book_appointment_missing_required_fields(client):
    """Returns 422 when required fields are missing."""
    resp = client.post("/api/webhooks/retell/book-appointment", json={})
    assert resp.status_code == 422


# ──────────────────────────────────────────────────────────────────────
# Full Retell pipeline: call_started → call_ended → call_analyzed
# ──────────────────────────────────────────────────────────────────────

def test_full_retell_pipeline(client, db):
    """Simulate a complete Retell call lifecycle and verify every record.

    1. call_started  → Lead created, Call created (status=answered)
    2. call_ended    → Call updated (status=completed, duration, recording)
    3. call_analyzed → Call updated (transcript, summary, outcome)
    4. book-appt     → Appointment linked to Lead + Call, Activity logged
    5. Dashboard     → KPIs reflect the real data
    """
    from datetime import datetime, timedelta, timezone
    from app.models.lead import Lead
    from app.models.call import Call
    from app.models.appointment import Appointment
    from app.models.activity import Activity
    from app.schemas.dashboard import DashboardResponse
    from app.services.dashboard_service import get_full_dashboard

    phone = "+15551112222"
    call_id_str = "retell_e2e_001"

    # ── Step 1: call_started ────────────────────────────────────────
    resp = client.post("/api/webhooks/retell", json={
        "event": "call_started",
        "call": {
            "call_id": call_id_str,
            "direction": "inbound",
            "caller_number": phone,
            "caller_name": "E2E Pipeline Test",
        },
    })
    assert resp.status_code == 200
    call_id = resp.json()["result"]["call_id"]
    lead_id = resp.json()["result"]["lead_id"]

    # Lead was created with real name and phone
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    assert lead is not None
    assert lead.first_name == "E2E"
    assert lead.last_name == "Pipeline Test"
    assert lead.phone == phone
    assert lead.status == "new"  # default

    # Call was created
    call = db.query(Call).filter(Call.id == call_id).first()
    assert call is not None
    assert call.external_call_id == call_id_str
    assert call.direction == "inbound"
    assert call.lead_id == lead_id
    assert call.status == "answered"

    # ── Step 2: call_ended ──────────────────────────────────────────
    resp = client.post("/api/webhooks/retell", json={
        "event": "call_ended",
        "call": {
            "call_id": call_id_str,
            "direction": "inbound",
            "caller_number": phone,
            "caller_name": "E2E Pipeline Test",
            "duration_ms": 120000,
            "recording_url": "https://retell.example.com/rec.wav",
        },
    })
    assert resp.status_code == 200
    assert resp.json()["result"]["status"] == "updated"

    db.expire_all()
    call = db.query(Call).filter(Call.id == call_id).first()
    assert call.status == "completed"
    assert call.duration_seconds == 120
    assert call.recording_url == "https://retell.example.com/rec.wav"

    # ── Step 3: call_analyzed ────────────────────────────────────────
    transcript_text = (
        "Caller: Hi, I need a roof inspection.\n"
        "AI: I'd be happy to help! When works for you?\n"
        "Caller: Next Tuesday at 10 AM.\n"
        "AI: Perfect, I'll book that for you."
    )
    resp = client.post("/api/webhooks/retell", json={
        "event": "call_analyzed",
        "call": {
            "call_id": call_id_str,
            "direction": "inbound",
            "transcript": transcript_text,
            "call_analysis": {
                "call_successful": True,
                "summary": "Customer booked a roof inspection for next Tuesday.",
            },
        },
    })
    assert resp.status_code == 200

    db.expire_all()
    call = db.query(Call).filter(Call.id == call_id).first()
    assert call.transcript == transcript_text
    assert call.summary == "Customer booked a roof inspection for next Tuesday."
    assert call.outcome == "qualified"  # call_successful=True

    # Lead updated to qualified
    db.expire_all()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    assert lead.status == "qualified"
    assert lead.temperature == "hot"

    # ── Step 4: book-appointment (via Custom Function) ───────────────
    appt_resp = client.post("/api/webhooks/retell/book-appointment", json={
        "customer_name": "E2E Pipeline Test",
        "customer_phone": phone,
        "start_time": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "title": "Roof Inspection",
        "lead_id": lead_id,
        "call_id": call_id,
    })
    assert appt_resp.status_code == 200
    appt_id = appt_resp.json()["appointment_id"]

    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    assert appt is not None
    assert appt.lead_id == lead_id
    assert appt.call_id == call_id
    assert appt.title == "Roof Inspection"
    assert appt.customer_phone == phone
    assert appt.status == "scheduled"

    # Activity record created
    activity = db.query(Activity).filter(
        Activity.entity_type == "appointment",
        Activity.entity_id == appt_id,
    ).first()
    assert activity is not None
    assert activity.type == "appointment_booked"

    # Lead status updated to appointment_booked
    db.expire_all()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    assert lead.status == "appointment_booked"

    # ── Step 5: Dashboard reflects the real data ─────────────────────
    dashboard = get_full_dashboard(db)
    assert isinstance(dashboard, DashboardResponse)
    assert dashboard.overview.total_calls >= 1
    assert dashboard.overview.total_leads >= 1
    assert dashboard.overview.appointments_booked >= 1
    assert dashboard.overview.conversion_rate > 0
    assert len(dashboard.recent_calls) >= 1
    assert len(dashboard.recent_activity) >= 1

def test_retell_call_ended_with_transcript(client, db):
    """Retell call_ended can carry a transcript directly."""
    from app.models.call import Call

    call_id_str = "retell_tx_001"

    client.post("/api/webhooks/retell", json={
        "event": "call_started",
        "call": {
            "call_id": call_id_str,
            "direction": "inbound",
            "caller_number": "+15552223333",
            "caller_name": "Transcript Test",
        },
    })

    resp = client.post("/api/webhooks/retell", json={
        "event": "call_ended",
        "call": {
            "call_id": call_id_str,
            "direction": "inbound",
            "duration_ms": 90000,
            "transcript": "Hello, I need help with my roof.",
        },
    })
    assert resp.status_code == 200

    db.expire_all()
    call = db.query(Call).filter(Call.external_call_id == call_id_str).first()
    assert call is not None
    assert call.status == "completed"
    assert call.transcript == "Hello, I need help with my roof."

def test_retell_call_started_captures_caller_name(client, db):
    """call_started with caller_name creates a lead with proper name."""
    from app.models.lead import Lead

    resp = client.post("/api/webhooks/retell", json={
        "event": "call_started",
        "call": {
            "call_id": "retell_name_001",
            "direction": "inbound",
            "caller_number": "+15553334444",
            "caller_name": "Maria Garcia",
        },
    })
    assert resp.status_code == 200
    lead_id = resp.json()["result"]["lead_id"]

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    assert lead.first_name == "Maria"
    assert lead.last_name == "Garcia"
    assert lead.phone == "+15553334444"

def test_demo_clear_endpoint(client, auth_headers, db):
    """POST /api/demo/clear wipes non-user data."""
    from app.models.lead import Lead
    from app.models.call import Call
    from app.models.appointment import Appointment
    from app.models.activity import Activity
    from app.models.user import User

    # Seed some data
    db.add(Lead(first_name="X", last_name="Y", phone="+1000", business_id=1))
    db.add(Call(direction="inbound", business_id=1))
    db.commit()
    assert db.query(Lead).count() >= 1
    assert db.query(Call).count() >= 1

    resp = client.post("/api/demo/clear", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "All data deleted (admin user preserved)"

    assert db.query(Lead).count() == 0
    assert db.query(Call).count() == 0
    assert db.query(Appointment).count() == 0
    assert db.query(Activity).count() == 0
    # Admin user still exists
    assert db.query(User).count() >= 1


# ──────────────────────────────────────────────────────────────────────
# Date normalization tests (smart year correction)
# ──────────────────────────────────────────────────────────────────────

def test_date_normalizer_unit_past_year_bumps_forward():
    """Unit test: 2024-09-18 with reference 2026-08-22 → 2026-09-18."""
    from datetime import datetime, timezone
    from app.utils.date_utils import normalize_appointment_date

    ref = datetime(2026, 8, 22, 9, 0, 0, tzinfo=timezone.utc)
    result = normalize_appointment_date("2024-09-18T11:00:00", reference=ref)
    assert result.year == 2026
    assert result.month == 9
    assert result.day == 18
    assert result.hour == 11
    assert result > ref

def test_date_normalizer_unit_past_year_month_also_past():
    """Unit test: 2024-08-10 with reference 2026-08-22 → 2027-08-10.

    August 10 is BEFORE August 22, so even 2026-08-10 is past.
    Must bump to 2027.
    """
    from datetime import datetime, timezone
    from app.utils.date_utils import normalize_appointment_date

    ref = datetime(2026, 8, 22, 9, 0, 0, tzinfo=timezone.utc)
    result = normalize_appointment_date("2024-08-10T11:00:00", reference=ref)
    assert result.year == 2027
    assert result.month == 8
    assert result.day == 10
    assert result > ref

def test_date_normalizer_unit_explicit_future_year():
    """Unit test: 2027-09-18 is already future → unchanged."""
    from datetime import datetime, timezone
    from app.utils.date_utils import normalize_appointment_date

    ref = datetime(2026, 8, 22, 9, 0, 0, tzinfo=timezone.utc)
    result = normalize_appointment_date("2027-09-18T11:00:00", reference=ref)
    assert result.year == 2027
    assert result.month == 9
    assert result.day == 18

def test_date_normalizer_unit_correct_future_date_unchanged():
    """Unit test: correct 2026-09-15 future date → unchanged."""
    from datetime import datetime, timezone
    from app.utils.date_utils import normalize_appointment_date

    ref = datetime(2026, 8, 22, 9, 0, 0, tzinfo=timezone.utc)
    result = normalize_appointment_date("2026-09-15T14:00:00", reference=ref)
    assert result.year == 2026
    assert result.month == 9
    assert result.day == 15

def test_date_normalizer_unit_invalid_iso_raises():
    """Unit test: invalid ISO string → ValueError."""
    from app.utils.date_utils import normalize_appointment_date

    try:
        normalize_appointment_date("not-a-date")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

def test_book_appointment_corrects_past_year(client):
    """A clearly-past year is normalized forward, keeping month/day/hour.

    Date-independent on purpose: the previous version hardcoded a target
    year that itself became past as real time advanced, which made the
    test fail for a reason unrelated to the code under test.
    """
    from datetime import datetime, timezone

    payload = {
        "customer_name": "Year Fix",
        "customer_phone": "+15550000001",
        "start_time": "2020-09-18T11:00:00",
        "title": "Inspection",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    stored = resp.json()["start_time"]
    parsed = datetime.fromisoformat(stored.replace("Z", "+00:00"))
    if parsed.tzinfo is None:  # SQLite returns naive datetimes
        parsed = parsed.replace(tzinfo=timezone.utc)
    # Bumped into the future...
    assert parsed > datetime.now(timezone.utc)
    # ...while preserving the caller's month/day/hour...
    assert (parsed.month, parsed.day, parsed.hour) == (9, 18, 11)
    # ...and never keeping the past year.
    assert parsed.year > 2020
    assert "2020" not in stored

def test_book_appointment_corrects_past_year_month_also_past(client):
    """Retell sends 2024-08-10 → normalizes to 2027-08-10.

    Aug 10 is before Aug 22, so even 2026-08-10 is past.
    Must bump to 2027.
    """
    payload = {
        "customer_name": "Year Fix 2",
        "customer_phone": "+15550000002",
        "start_time": "2024-08-10T11:00:00",
        "title": "Inspection",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "2027-08-10" in body["start_time"]

def test_book_appointment_explicit_future_year_accepted(client):
    """2027-09-18 is explicitly future → accepted as-is."""
    payload = {
        "customer_name": "Future Year",
        "customer_phone": "+15550000003",
        "start_time": "2027-09-18T11:00:00",
        "title": "Inspection",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "2027-09-18" in body["start_time"]

def test_book_appointment_invalid_iso_rejected(client):
    """Invalid ISO string → 422."""
    payload = {
        "customer_name": "Bad Date",
        "customer_phone": "+15550000004",
        "start_time": "not-a-date",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 422

def test_book_appointment_accepts_future_date(client):
    """Future start_time must be accepted unchanged."""
    from datetime import datetime, timedelta, timezone
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    payload = {
        "customer_name": "Future Date",
        "customer_phone": "+15550000005",
        "start_time": tomorrow,
        "title": "Inspection",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_book_appointment_yesterday_normalizes_forward(client):
    """Yesterday's date → normalized to next year's occurrence."""
    from datetime import datetime, timedelta, timezone
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1))
    # Strip timezone for the raw string (Retell sends naive datetimes)
    raw = yesterday.replace(tzinfo=None).isoformat()
    payload = {
        "customer_name": "Yesterday Fix",
        "customer_phone": "+15550000006",
        "start_time": raw,
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    # The date should be in the future
    from app.utils.date_utils import normalize_appointment_date
    result = normalize_appointment_date(raw)
    assert result > datetime.now(timezone.utc)


def test_book_appointment_auto_creates_lead_and_call(client, db):
    """When lead_id/call_id not provided, book-appointment creates them."""
    from datetime import datetime, timedelta, timezone
    from app.models.lead import Lead
    from app.models.call import Call
    from app.models.appointment import Appointment
    from app.models.activity import Activity

    payload = {
        "customer_name": "Ayan Khan",
        "customer_phone": "+923189015613",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=14)).isoformat(),
        "title": "Roof Inspection",
        "notes": "House 15, Islamabad",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    body = resp.json()

    # Response contains lead_id and call_id
    assert body["lead_id"] is not None
    assert body["call_id"] is not None
    assert body["appointment_id"] is not None

    # Lead was created
    lead = db.query(Lead).filter(Lead.id == body["lead_id"]).first()
    assert lead is not None
    assert lead.first_name == "Ayan"
    assert lead.last_name == "Khan"
    assert lead.phone == "+923189015613"
    assert lead.status == "appointment_booked"
    assert lead.temperature == "hot"
    assert lead.source == "inbound_call"

    # Call was created
    call = db.query(Call).filter(Call.id == body["call_id"]).first()
    assert call is not None
    assert call.direction == "inbound"
    assert call.lead_id == lead.id
    assert call.status == "completed"
    assert call.outcome == "appointment_booked"
    assert call.appointment_booked == "1"

    # Appointment is linked to both
    appt = db.query(Appointment).filter(Appointment.id == body["appointment_id"]).first()
    assert appt.lead_id == lead.id
    assert appt.call_id == call.id
    assert appt.customer_name == "Ayan Khan"
    assert appt.customer_phone == "+923189015613"
    assert appt.title == "Roof Inspection"

    # Activity logged
    activity = db.query(Activity).filter(
        Activity.entity_type == "appointment",
        Activity.entity_id == appt.id,
    ).first()
    assert activity is not None
    assert activity.type == "appointment_booked"

def test_book_appointment_reuses_existing_lead_by_phone(client, db):
    """If a lead with the same phone exists, it should be reused."""
    from datetime import datetime, timedelta, timezone
    from app.models.lead import Lead

    # Pre-create a lead
    lead = Lead(first_name="Existing", last_name="Lead", phone="+19999999999")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    old_lead_id = lead.id

    payload = {
        "customer_name": "Existing Lead",
        "customer_phone": "+19999999999",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        "title": "Follow-up",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200
    body = resp.json()

    # Should reuse the existing lead
    assert body["lead_id"] == old_lead_id
    # Status should be updated
    db.expire_all()
    lead = db.query(Lead).filter(Lead.id == old_lead_id).first()
    assert lead.status == "appointment_booked"

def test_book_appointment_after_clear_shows_in_dashboard(client, db, auth_headers):
    """After clearing data and booking an appointment, dashboard reflects real data."""
    from datetime import datetime, timedelta, timezone
    from app.services.dashboard_service import get_full_dashboard
    from app.schemas.dashboard import DashboardResponse

    # Book an appointment (creates lead + call + appointment)
    payload = {
        "customer_name": "Dashboard Test",
        "customer_phone": "+15557778888",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "title": "Test Appointment",
    }
    resp = client.post("/api/webhooks/retell/book-appointment", json=payload)
    assert resp.status_code == 200

    # Dashboard should now show real data
    dashboard = get_full_dashboard(db)
    assert isinstance(dashboard, DashboardResponse)
    assert dashboard.overview.total_calls >= 1
    assert dashboard.overview.total_leads >= 1
    assert dashboard.overview.appointments_booked >= 1
    assert dashboard.overview.conversion_rate > 0
