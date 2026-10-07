"""Test configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_db
from app.main import app
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.business import Business

# Test database
SQLALCHEMY_TEST_URL = "sqlite:///./test_voiceflow.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Get a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Get a test HTTP client."""
    return TestClient(app)


@pytest.fixture
def test_user(db):
    """Create a test user and return it with a token."""
    user = User(
        name="Test Admin",
        email="test@voiceflow.ai",
        password_hash=hash_password("test123"),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_business(db):
    """Create a test business."""
    business = Business(
        name="Test Roofing Co",
        industry="Home Services",
        phone="+15551002000",
        email="test@roofing.com",
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@pytest.fixture
def auth_headers(test_user):
    """Get auth headers for the test user."""
    token = create_access_token(data={"sub": str(test_user.id), "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}
