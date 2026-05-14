import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.models import *  # noqa: F401, F403
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

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
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── EducationInstitution ──────────────────────────────────────────────────────

def test_create_education_institution(client):
    response = client.post(
        "/api/v1/education-institutions",
        json={"name": "UNISINOS", "is_active": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "UNISINOS"
    assert data["id"] is not None


def test_list_education_institutions(client):
    client.post("/api/v1/education-institutions", json={"name": "UNISINOS"})
    response = client.get("/api/v1/education-institutions")
    assert response.status_code == 200
    assert len(response.json()) >= 1


# ── HealthCenter ──────────────────────────────────────────────────────────────

def test_create_health_center(client):
    response = client.post(
        "/api/v1/health-centers",
        json={"name": "UBS Centro", "is_active": True},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "UBS Centro"


def test_get_health_center_not_found(client):
    response = client.get("/api/v1/health-centers/999")
    assert response.status_code == 404


# ── Room ──────────────────────────────────────────────────────────────────────

def test_create_room(client):
    hc = client.post("/api/v1/health-centers", json={"name": "UBS Norte"}).json()
    response = client.post(
        "/api/v1/rooms",
        json={
            "health_center_id": hc["id"],
            "name": "Sala 01",
            "room_capacity": 5,
            "has_gurney": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["has_gurney"] is True


# ── Course ────────────────────────────────────────────────────────────────────

def test_create_course(client):
    inst = client.post("/api/v1/education-institutions", json={"name": "PUCRS"}).json()
    response = client.post(
        "/api/v1/courses",
        json={
            "edu_institution_id": inst["id"],
            "name": "Enfermagem",
            "requires_gurney": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["requires_gurney"] is True


# ── Student ───────────────────────────────────────────────────────────────────

def test_create_student(client):
    inst = client.post("/api/v1/education-institutions", json={"name": "FEEVALE"}).json()
    course = client.post(
        "/api/v1/courses",
        json={"edu_institution_id": inst["id"], "name": "Fisioterapia", "requires_gurney": False},
    ).json()
    response = client.post(
        "/api/v1/students",
        json={"edu_institute_id": inst["id"], "course_id": course["id"], "status": "PENDING"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"
