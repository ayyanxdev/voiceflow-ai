"""Authentication tests."""

import pytest

from app.core.security import hash_password, create_access_token
from app.models.user import User


# ---------------------------------------------------------------------------
# Basic login tests (existing)
# ---------------------------------------------------------------------------

def test_login_success(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "test@voiceflow.ai",
        "password": "test123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@voiceflow.ai"


def test_login_wrong_password(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "test@voiceflow.ai",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/api/auth/login", json={
        "email": "nobody@email.com",
        "password": "test123",
    })
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Demo admin credential tests
# ---------------------------------------------------------------------------

@pytest.fixture
def demo_admin(db):
    """Create the demo admin user with the documented credentials."""
    user = User(
        name="Admin User",
        email="admin@voiceflow.ai",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active="1",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_demo_admin_login_success(client, demo_admin):
    """admin@voiceflow.ai / admin123 must return 200 + valid JWT."""
    response = client.post("/api/auth/login", json={
        "email": "admin@voiceflow.ai",
        "password": "admin123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@voiceflow.ai"
    assert data["user"]["role"] == "admin"
    assert data["token_type"] == "bearer"


def test_demo_admin_wrong_password_returns_401(client, demo_admin):
    """Wrong password for demo admin must return 401."""
    response = client.post("/api/auth/login", json={
        "email": "admin@voiceflow.ai",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_demo_admin_nonexistent_email_returns_401(client):
    """Login with unknown email must return 401."""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@voiceflow.ai",
        "password": "admin123",
    })
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Inactive user rejection
# ---------------------------------------------------------------------------

@pytest.fixture
def inactive_admin(db):
    """Create an inactive admin user."""
    user = User(
        name="Inactive Admin",
        email="inactive@voiceflow.ai",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active="0",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_inactive_user_rejected(client, inactive_admin):
    """Inactive user must be rejected (401 or 403)."""
    response = client.post("/api/auth/login", json={
        "email": "inactive@voiceflow.ai",
        "password": "admin123",
    })
    assert response.status_code in [401, 403]


# ---------------------------------------------------------------------------
# JWT / token validation
# ---------------------------------------------------------------------------

def test_get_current_user(client, test_user, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@voiceflow.ai"


def test_unauthorized_access(client):
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]


def test_invalid_token_returns_401(client):
    """A malformed JWT must be rejected."""
    headers = {"Authorization": "Bearer not-a-real-token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401


def test_valid_jwt_contains_expected_claims(client, demo_admin):
    """Successful login returns a JWT decodable by the backend."""
    response = client.post("/api/auth/login", json={
        "email": "admin@voiceflow.ai",
        "password": "admin123",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Use the token to call /me
    me_response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "admin@voiceflow.ai"
    assert me_response.json()["role"] == "admin"
