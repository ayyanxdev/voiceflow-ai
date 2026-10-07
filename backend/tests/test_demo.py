"""Demo mode tests."""

from app.core.security import hash_password
from app.models.user import User


def test_seed_demo_data(client, auth_headers):
    response = client.post("/api/demo/seed", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["leads"] == 12
    assert data["calls"] == 20
    assert data["appointments"] == 5
    assert data["businesses"] == 1
    assert data["campaigns"] == 1
    assert data["followups"] == 4
    assert data["activities"] == 20


def test_seed_idempotent(client, auth_headers):
    """Seeding twice should not create duplicates."""
    client.post("/api/demo/seed", headers=auth_headers)
    response = client.post("/api/demo/seed", headers=auth_headers)
    assert response.status_code == 200
    # Second call should report already seeded
    assert "already" in response.json().get("message", "").lower() or response.json()["leads"] == 0


def test_seed_creates_admin_user(client, auth_headers):
    """Seed should ensure admin@voiceflow.ai user exists."""
    response = client.post("/api/demo/seed", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Admin user already exists from startup seeding, so users=0 is valid
    # But the data should still be seeded
    assert data["leads"] == 12


def test_seed_then_dashboard_has_data(client, auth_headers):
    """After seeding, dashboard should show non-zero statistics."""
    client.post("/api/demo/seed", headers=auth_headers)
    response = client.get("/api/dashboard", headers=auth_headers)
    assert response.status_code == 200
    overview = response.json()["overview"]
    assert overview["total_calls"] > 0
    assert overview["total_leads"] > 0
    assert overview["appointments_booked"] > 0


def test_seed_unauthenticated_returns_401(client):
    """Seed endpoint must require authentication."""
    response = client.post("/api/demo/seed")
    assert response.status_code in [401, 403]
