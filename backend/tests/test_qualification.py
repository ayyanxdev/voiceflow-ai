"""Lead qualification scoring tests."""

from app.services.lead_service import calculate_qualification_score, calculate_temperature


def test_empty_lead_scores_low():
    score = calculate_qualification_score({})
    assert score == 0
    assert calculate_temperature(score) == "cold"


def test_lead_with_phone():
    score = calculate_qualification_score({"phone": "+15551234567"})
    assert score >= 20
    assert calculate_temperature(score) in ("cold", "warm")


def test_lead_with_complete_contact():
    score = calculate_qualification_score({
        "phone": "+15551234567",
        "email": "test@test.com",
    })
    assert score >= 30


def test_lead_with_company():
    score = calculate_qualification_score({"company": "Acme Corp"})
    assert score >= 10


def test_interested_lead():
    score = calculate_qualification_score({"notes": "Very interested in the service"})
    assert score >= 20


def test_appointment_requested():
    score = calculate_qualification_score({"notes": "Wants to schedule an appointment"})
    assert score >= 30


def test_qualified_status():
    score = calculate_qualification_score({"status": "qualified"})
    assert score >= 20


def test_hot_lead_score():
    score = calculate_qualification_score({
        "phone": "+15551234567",
        "email": "hot@test.com",
        "company": "Hot Lead Inc",
        "status": "qualified",
        "notes": "Very interested and wants to schedule appointment",
    })
    assert score >= 70
    assert calculate_temperature(score) == "hot"


def test_score_never_exceeds_100():
    score = calculate_qualification_score({
        "phone": "+15551234567",
        "email": "max@test.com",
        "company": "Max Corp",
        "status": "qualified",
        "notes": "Interested in pricing and wants to schedule appointment immediately",
    })
    assert score <= 100
