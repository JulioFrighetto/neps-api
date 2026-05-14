import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.models import *  # noqa: F401, F403
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _seed_and_login(client, email="admin@test.com", password="secret123"):
    from app.domains.user.repository import create
    from app.domains.user.schemas import UserCreate

    db = next(app.dependency_overrides[get_db]())
    create(db, UserCreate(name="Admin", email=email, password=password))

    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_login_success(client):
    tokens = _seed_and_login(client)
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_wrong_password(client):
    _seed_and_login(client)
    resp = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/api/v1/auth/login", json={"email": "none@test.com", "password": "x"})
    assert resp.status_code == 401


def test_me_authenticated(client):
    tokens = _seed_and_login(client)
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@test.com"


def test_me_unauthenticated(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 403


def test_me_invalid_token(client):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


def test_refresh_token(client):
    tokens = _seed_and_login(client)
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refresh_with_access_token_rejected(client):
    tokens = _seed_and_login(client)
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert resp.status_code == 401


def test_create_user(client):
    resp = client.post("/api/v1/users/", json={"name": "Novo", "email": "novo@test.com", "password": "pass123"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "novo@test.com"
    assert "password" not in resp.json()


def test_duplicate_email_rejected(client):
    client.post("/api/v1/users/", json={"name": "A", "email": "dup@test.com", "password": "pass"})
    resp = client.post("/api/v1/users/", json={"name": "B", "email": "dup@test.com", "password": "pass"})
    assert resp.status_code == 409


def test_change_password(client):
    tokens = _seed_and_login(client, email="u@test.com", password="oldpass")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = client.get("/api/v1/auth/me", headers=headers).json()

    resp = client.post(
        f"/api/v1/users/{me['id']}/change-password",
        json={"current_password": "oldpass", "new_password": "newpass"},
        headers=headers,
    )
    assert resp.status_code == 204

    assert client.post("/api/v1/auth/login", json={"email": "u@test.com", "password": "oldpass"}).status_code == 401
    assert client.post("/api/v1/auth/login", json={"email": "u@test.com", "password": "newpass"}).status_code == 200


def test_update_other_user_forbidden(client):
    _seed_and_login(client, email="user1@test.com", password="pass1")
    tokens2 = _seed_and_login(client, email="user2@test.com", password="pass2")
    headers2 = {"Authorization": f"Bearer {tokens2['access_token']}"}

    user1 = client.get("/api/v1/users/1").json()
    resp = client.patch(f"/api/v1/users/{user1['id']}", json={"name": "Hacked"}, headers=headers2)
    assert resp.status_code == 403
