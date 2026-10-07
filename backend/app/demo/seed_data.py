"""Demo data seeding for VoiceFlow AI."""

import json
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.models.business import Business
from app.models.lead import Lead
from app.models.call import Call
from app.models.appointment import Appointment
from app.models.campaign import Campaign
from app.models.followup import FollowUp
from app.models.activity import Activity


def seed_demo_data(db: Session) -> dict:
    """Seed database with realistic demo data. Idempotent — safe to run multiple times."""
    result = {"users": 0, "businesses": 0, "leads": 0, "calls": 0,
              "appointments": 0, "campaigns": 0, "followups": 0, "activities": 0}

    # Ensure the admin user exists with a valid password hash.
    admin = db.query(User).filter(User.email == "admin@voiceflow.ai").first()
    if admin is None:
        admin = User(
            name="Admin User",
            email="admin@voiceflow.ai",
            password_hash=hash_password("admin123"),
            role="admin",
        )
        db.add(admin)
        db.flush()
        result["users"] = 1
    elif not verify_password("admin123", admin.password_hash):
        admin.password_hash = hash_password("admin123")
        db.commit()

    # Check if demo business data already exists
    existing_business = db.query(Business).first()
    if existing_business:
        return {"message": "Demo data already seeded", **result}

    now = datetime.now(timezone.utc)

    # === BUSINESS ===
    business = Business(
        name="Elite Roofing",
        industry="Home Services / Roofing",
        phone="+1 (555) 100-2000",
        email="info@eliteroofing.com",
        website="https://eliteroofing.com",
        address="123 Main St, Dallas, TX 75201",
        timezone="America/Chicago",
        business_hours=json.dumps({"mon-fri": "8am-6pm", "sat": "9am-2pm"}),
        description="Premium roofing services for residential and commercial properties.",
        owner_id=admin.id,
    )
    db.add(business)
    db.flush()
    result["businesses"] = 1

    # === LEADS ===
    leads_data = [
        {"first_name": "Sarah", "last_name": "Johnson", "phone": "+1 555 010 1234", "email": "sarah.j@email.com", "company": "", "source": "inbound_call", "status": "qualified", "temperature": "hot", "qualification_score": 87, "notes": "Interested in roof inspection. Has storm damage. Ready to schedule."},
        {"first_name": "Michael", "last_name": "Smith", "phone": "+1 555 020 2345", "email": "m.smith@email.com", "company": "Smith Properties", "source": "inbound_call", "status": "qualified", "temperature": "hot", "qualification_score": 82, "notes": "Commercial property owner. Needs full roof replacement estimate."},
        {"first_name": "John", "last_name": "Davis", "phone": "+1 555 030 3456", "email": "jdavis@email.com", "company": "", "source": "outbound", "status": "lost", "temperature": "cold", "qualification_score": 22, "notes": "Not interested at this time. May revisit next year."},
        {"first_name": "Emily", "last_name": "Brown", "phone": "+1 555 040 4567", "email": "emily.brown@email.com", "company": "", "source": "inbound_call", "status": "appointment_booked", "temperature": "hot", "qualification_score": 91, "notes": "Urgent leak repair needed. Booked emergency inspection."},
        {"first_name": "Robert", "last_name": "Wilson", "phone": "+1 555 050 5678", "email": "rwilson@email.com", "company": "Wilson Construction", "source": "import", "status": "new", "temperature": "warm", "qualification_score": 45, "notes": "Imported from Google Sheets. Interested in commercial services."},
        {"first_name": "Jennifer", "last_name": "Taylor", "phone": "+1 555 060 6789", "email": "jtaylor@email.com", "company": "", "source": "website", "status": "contacted", "temperature": "warm", "qualification_score": 55, "notes": "Submitted web form. Asked about pricing for gutter installation."},
        {"first_name": "David", "last_name": "Anderson", "phone": "+1 555 070 7890", "email": "danderson@email.com", "company": "Anderson LLC", "source": "inbound_call", "status": "qualified", "temperature": "hot", "qualification_score": 78, "notes": "Needs re-roofing. Insurance claim in progress. Budget $15k-25k."},
        {"first_name": "Lisa", "last_name": "Martinez", "phone": "+1 555 080 8901", "email": "lisa.m@email.com", "company": "", "source": "inbound_call", "status": "follow_up", "temperature": "warm", "qualification_score": 60, "notes": "Wants to compare quotes. Will call back next week."},
        {"first_name": "James", "last_name": "Garcia", "phone": "+1 555 090 9012", "email": "jgarcia@email.com", "company": "", "source": "outbound", "status": "new", "temperature": "cold", "qualification_score": 30, "notes": "Lead from marketing campaign. Initial contact attempted."},
        {"first_name": "Amanda", "last_name": "Clark", "phone": "+1 555 100 0123", "email": "aclark@email.com", "company": "Clark Enterprises", "source": "inbound_call", "status": "converted", "temperature": "hot", "qualification_score": 95, "notes": "Full roof replacement completed. Very satisfied customer."},
        {"first_name": "Chris", "last_name": "Rodriguez", "phone": "+1 555 110 1234", "email": "crodriguez@email.com", "company": "", "source": "inbound_call", "status": "unqualified", "temperature": "cold", "qualification_score": 15, "notes": "Wrong number - not looking for roofing services."},
        {"first_name": "Maria", "last_name": "Lewis", "phone": "+1 555 120 2345", "email": "maria.lewis@email.com", "company": "", "source": "website", "status": "new", "temperature": "warm", "qualification_score": 50, "notes": "Submitted inquiry about roof maintenance program."},
    ]

    leads = []
    for ld in leads_data:
        lead = Lead(business_id=business.id, **ld)
        db.add(lead)
        leads.append(lead)
    db.flush()
    result["leads"] = len(leads)

    # === CALLS ===
    transcripts = [
        "Caller: Hi, I need someone to inspect my roof.\nAI: Hello! I'd be happy to help you with a roof inspection. Can I get your name?\nCaller: Sure, it's Sarah Johnson.\nAI: Thank you, Sarah. What prompted you to seek an inspection?\nCaller: We had a storm last week and I noticed some missing shingles.\nAI: I understand. Storm damage can be serious. When would be a good time for our inspector to visit?\nCaller: How about next Tuesday morning?\nAI: Perfect, I have a slot available at 10 AM next Tuesday. I'll book that for you.\nCaller: Great, thank you!",
        "Caller: Hello, I'm calling about getting an estimate for a new roof.\nAI: Welcome! I'd be happy to help. May I have your name?\nCaller: Michael Smith.\nAI: Hi Michael. What type of property are you looking to have roofed?\nCaller: It's a commercial building, about 5,000 square feet.\nAI: Perfect, we handle commercial projects. I'll schedule a consultation for you.\nCaller: Sounds good. What's your pricing like?\nAI: Our commercial estimates are free and typically range based on material and scope. Shall I schedule an on-site estimate?\nCaller: Yes please.",
        "Caller: Yeah, I got a call about roofing services but I'm not really interested right now.\nAI: No problem at all, John. If your needs change in the future, we're here to help. Have a great day!\nCaller: Thanks, goodbye.",
        "Caller: I have a really bad leak in my kitchen ceiling! I think it's from the roof.\nAI: I understand this is urgent. Let me help you right away. Can I get your name?\nCaller: Emily Brown.\nAI: Emily, I'm scheduling an emergency inspection for you. When can someone come out?\nCaller: Today if possible!\nAI: I have an opening this afternoon at 2 PM. Does that work?\nCaller: Yes, absolutely!",
        "Caller: Hi, I saw your ad online. I'm thinking about getting my roof replaced.\nAI: Great to hear from you! Can I get your name?\nCaller: David Anderson.\nAI: David, are you dealing with any specific issues with your current roof?\nCaller: It's about 20 years old and my insurance company wants an inspection.\nAI: That's common. We work with insurance claims regularly. I'll schedule an inspection that can support your claim.\nCaller: That would be excellent.",
        "Caller: I was wondering about your pricing for gutter cleaning.\nAI: Hi there! We offer gutter cleaning starting at $150. Can I get your name?\nCaller: Lisa Martinez.\nAI: Hi Lisa. Would you like to schedule a gutter cleaning service?\nCaller: I'd like to think about it and compare some prices first.\nAI: Of course. Can I have your number to follow up next week?\nCaller: Sure, it's on file.",
    ]

    outcomes = [
        ("completed", "appointment_booked", "positive"),
        ("completed", "qualified", "positive"),
        ("completed", "not_interested", "neutral"),
        ("completed", "qualified", "positive"),
        ("completed", "information_request", "neutral"),
        ("completed", "callback_requested", "neutral"),
        ("completed", "qualified", "positive"),
        ("completed", "callback_requested", "neutral"),
        ("completed", "wrong_number", "negative"),
        ("completed", "qualified", "positive"),
        ("completed", "not_interested", "negative"),
        ("completed", "information_request", "neutral"),
        ("completed", "appointment_booked", "positive"),
        ("completed", "qualified", "positive"),
        ("completed", "no_answer", "negative"),
        ("completed", "qualified", "positive"),
        ("completed", "not_interested", "neutral"),
        ("completed", "callback_requested", "neutral"),
        ("completed", "appointment_booked", "positive"),
        ("completed", "information_request", "neutral"),
    ]

    calls = []
    for i in range(20):
        days_ago = random.randint(0, 14)
        start = now - timedelta(days=days_ago, hours=random.randint(0, 12))
        duration = random.randint(60, 360)
        end = start + timedelta(seconds=duration)
        direction = "inbound" if random.random() > 0.3 else "outbound"
        status_val, outcome_val, sentiment_val = outcomes[i % len(outcomes)]
        transcript = transcripts[i % len(transcripts)]
        lead_idx = i % len(leads)

        call = Call(
            business_id=business.id,
            lead_id=leads[lead_idx].id,
            external_call_id=f"demo_call_{i+1:04d}",
            direction=direction,
            status="completed",
            outcome=outcome_val,
            started_at=start,
            ended_at=end,
            duration_seconds=duration,
            transcript=transcript,
            summary=f"AI agent handled {'inbound' if direction == 'inbound' else 'outbound'} call. Outcome: {outcome_val.replace('_', ' ')}.",
            sentiment=sentiment_val,
            qualification_score=random.randint(10, 95),
            appointment_booked="1" if outcome_val == "appointment_booked" else "0",
            transferred_to_human="0",
            created_at=start,
        )
        db.add(call)
        calls.append(call)
    db.flush()
    result["calls"] = len(calls)

    # === APPOINTMENTS ===
    appt_data = [
        ("Roof Inspection - Sarah Johnson", "Sarah Johnson", "+1 555 010 1234", "sarah.j@email.com", "scheduled"),
        ("Emergency Roof Repair - Emily Brown", "Emily Brown", "+1 555 040 4567", "emily.brown@email.com", "confirmed"),
        ("Commercial Estimate - Michael Smith", "Michael Smith", "+1 555 020 2345", "m.smith@email.com", "scheduled"),
        ("Insurance Inspection - David Anderson", "David Anderson", "+1 555 070 7890", "danderson@email.com", "completed"),
        ("Roof Replacement Consult - Amanda Clark", "Amanda Clark", "+1 555 100 0123", "aclark@email.com", "completed"),
    ]

    appointments = []
    for i, (title, cname, cphone, cemail, appt_status) in enumerate(appt_data):
        if appt_status == "completed":
            start = now - timedelta(days=random.randint(1, 7), hours=random.randint(9, 16))
        else:
            start = now + timedelta(days=random.randint(1, 14), hours=random.randint(9, 16))
        end = start + timedelta(hours=1)

        appt = Appointment(
            business_id=business.id,
            lead_id=leads[i].id,
            call_id=calls[i].id if i < len(calls) else None,
            title=title,
            customer_name=cname,
            customer_phone=cphone,
            customer_email=cemail,
            start_time=start,
            end_time=end,
            status=appt_status,
            notes=f"Auto-scheduled by AI agent for {title.lower()}",
            created_at=start - timedelta(days=1),
        )
        db.add(appt)
        appointments.append(appt)
    db.flush()
    result["appointments"] = len(appointments)

    # === CAMPAIGN ===
    campaign = Campaign(
        business_id=business.id,
        name="Roofing Lead Outreach",
        description="Outbound campaign targeting leads from recent marketing efforts.",
        status="completed",
        total_leads=6,
        completed_calls=6,
        qualified_leads=3,
        appointments=2,
        created_at=now - timedelta(days=10),
    )
    db.add(campaign)
    db.flush()
    result["campaigns"] = 1

    # === FOLLOW-UPS ===
    followup_data = [
        (leads[0].id, calls[0].id, "sms", "pending", "Thank you for your call, Sarah! Your inspection is confirmed for Tuesday at 10 AM."),
        (leads[1].id, calls[1].id, "email", "sent", "Hi Michael, here is the commercial roofing estimate we discussed."),
        (leads[5].id, calls[5].id, "call", "pending", "Follow up with Lisa about gutter cleaning pricing."),
        (leads[7].id, calls[7].id, "call", "pending", "Call Lisa back next week to discuss gutter installation options."),
    ]

    for lead_id, call_id, ftype, fstatus, message in followup_data:
        fu = FollowUp(
            business_id=business.id,
            lead_id=lead_id,
            call_id=call_id,
            type=ftype,
            scheduled_at=now + timedelta(days=random.randint(1, 5)),
            status=fstatus,
            message=message,
            created_at=now - timedelta(days=random.randint(1, 3)),
        )
        db.add(fu)
    db.flush()
    result["followups"] = len(followup_data)

    # === ACTIVITY LOG ===
    activity_data = [
        ("call_received", "New inbound call from Sarah Johnson"),
        ("lead_created", "Lead created: Sarah Johnson"),
        ("appointment_booked", "Appointment booked: Roof Inspection"),
        ("call_completed", "Call completed with Sarah Johnson - Appointment Booked"),
        ("lead_qualified", "Lead qualified: Michael Smith (Score: 82)"),
        ("follow_up_scheduled", "Follow-up scheduled for Sarah Johnson"),
        ("call_completed", "Call completed with John Davis - Not Interested"),
        ("lead_created", "Lead created: Emily Brown"),
        ("call_received", "Urgent call from Emily Brown - Emergency repair"),
        ("appointment_booked", "Emergency appointment booked: Emily Brown"),
        ("campaign_started", "Campaign started: Roofing Lead Outreach"),
        ("call_completed", "Outbound call completed - David Anderson"),
        ("lead_qualified", "Lead qualified: David Anderson (Score: 78)"),
        ("campaign_completed", "Campaign completed: Roofing Lead Outreach"),
        ("call_completed", "Call completed - Amanda Clark - Converted!"),
        ("crm_sync", "CRM sync completed: 3 contacts updated"),
        ("webhook_received", "Retell webhook processed: call_ended event"),
        ("call_completed", "Inbound call from Lisa Martinez - Callback requested"),
        ("lead_created", "Lead created: Chris Rodriguez (Wrong number)"),
        ("call_completed", "Outbound call completed - Robert Wilson - New lead"),
    ]

    for i, (atype, desc) in enumerate(activity_data):
        act = Activity(
            business_id=business.id,
            type=atype,
            description=desc,
            entity_type=atype.split("_")[0] if "_" in atype else None,
            entity_id=leads[i % len(leads)].id if i < len(leads) else None,
            created_at=now - timedelta(hours=random.randint(0, 72)),
        )
        db.add(act)
    db.flush()
    result["activities"] = len(activity_data)

    db.commit()

    return {"message": "Demo data seeded successfully", **result}
