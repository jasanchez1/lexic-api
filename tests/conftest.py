# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app


@pytest.fixture
def test_db():
    """
    Create a test database in memory
    """
    # Create SQLite in-memory database for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Dependency override
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal


@pytest.fixture
def client(test_db):
    """
    Create a test client for FastAPI
    """
    with TestClient(app) as client:
        yield client


# tests/test_health.py
def test_health_check(client):
    """
    Test health check endpoint
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "message" in response.json()


def test_db_health_check(client):
    """
    Test database health check endpoint
    """
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "message" in response.json()


# tests/test_auth.py
def test_signup(client):
    """
    Test user signup
    """
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert "user_id" in data


def test_login(client):
    """
    Test user login
    """
    # First create a user
    client.post(
        "/auth/signup",
        json={
            "email": "login@example.com",
            "password": "password123",
            "first_name": "Login",
            "last_name": "User"
        },
    )
    
    # Then try to login
    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert "user_id" in data


def test_me(client):
    """
    Test get current user endpoint
    """
    # First create a user and get token
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "me@example.com",
            "password": "password123",
            "first_name": "Me",
            "last_name": "User"
        },
    )
    access_token = signup_response.json()["access_token"]
    
    # Then try to get current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["first_name"] == "Me"
    assert data["last_name"] == "User"