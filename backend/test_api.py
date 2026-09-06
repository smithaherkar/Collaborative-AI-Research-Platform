"""
Automated unit and integration test suite for the FastAPI backend.

Tests cover:
- Health check availability
- User signup, duplicate registration prevention, and login
- JWT token issuance and invalid credential handling
- Protected route authorization checks
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# Isolated in-memory SQLite database for running fast, repeatable tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Dependency override providing isolated in-memory test database sessions."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply test database override and create schema
app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)

# Test client
client = TestClient(app)


def test_health_check():
    """Verifies that the root health endpoint responds with 200 OK and status message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Collaborative AI Research Platform" in data["message"]


def test_signup_and_login_flow():
    """Tests the full user lifecycle: registration, duplicate rejection, and login."""
    # 1. Register a new user
    signup_res = client.post("/signup", json={
        "email": "researcher@example.com",
        "password": "securepassword123"
    })
    assert signup_res.status_code == 201
    user_data = signup_res.json()
    assert user_data["email"] == "researcher@example.com"
    assert "id" in user_data

    # 2. Verify duplicate email is rejected with 400 Bad Request
    duplicate_res = client.post("/signup", json={
        "email": "researcher@example.com",
        "password": "securepassword123"
    })
    assert duplicate_res.status_code == 400
    assert "already exists" in duplicate_res.json()["detail"]

    # 3. Verify bad credentials return 401 Unauthorized
    invalid_login = client.post("/login", json={
        "email": "researcher@example.com",
        "password": "wrongpassword"
    })
    assert invalid_login.status_code == 401

    # 4. Successful login returns a Bearer JWT
    login_res = client.post("/login", json={
        "email": "researcher@example.com",
        "password": "securepassword123"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 5. Accessing protected endpoint with the Bearer token succeeds
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    my_reports_res = client.get("/my-reports", headers=headers)
    assert my_reports_res.status_code == 200
    assert isinstance(my_reports_res.json(), list)


def test_unauthorized_access():
    """Verifies that protected routes reject unauthenticated requests with 401."""
    res_reports = client.get("/my-reports")
    assert res_reports.status_code == 401

    res_report_by_id = client.get("/reports/1")
    assert res_report_by_id.status_code == 401
