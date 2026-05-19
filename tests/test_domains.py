import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.models import *  # noqa: F401, F403
from app.main import app
from app.domains.service.model import Service
from app.domains.user.model import User

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


# ── EducationInstitute ──────────────────────────────────────────────────────

def test_create_education_institute(client):
    response = client.post(
        "/api/v1/education-institutes",
        json={"name": "UNISINOS", "is_active": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "UNISINOS"
    assert data["id"] is not None


def test_list_education_institutes(client):
    client.post("/api/v1/education-institutes", json={"name": "UNISINOS"})
    response = client.get("/api/v1/education-institutes")
    assert response.status_code == 200
    assert len(response.json()) >= 1


# ── Room ──────────────────────────────────────────────────────────────────────




# ── Services ────────────────────────────────────────────────────────────────

def test_create_service(client):
    response = client.post(
        "/api/v1/services",
        json={
            "name": "Serviço Norte",
            "is_active": True,
            "user_name": "Service Norte",
            "user_email": "service-norte@neps.com",
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Serviço Norte"


def test_create_service_creates_user(client, db, monkeypatch):
    monkeypatch.setattr("app.domains.service.router.send_email", lambda *args, **kwargs: None)

    response = client.post(
        "/api/v1/services",
        json={
            "name": "Serviço Centro",
            "is_active": True,
            "user_name": "Service Centro",
            "user_email": "service-centro@neps.com",
        },
    )

    assert response.status_code == 201
    service = db.query(Service).filter(Service.name == "Serviço Centro").first()
    assert service is not None
    user = db.query(User).filter(User.service_id == service.id).first()
    assert user is not None
    assert user.role == "service"
    assert user.email == "service-centro@neps.com"


def test_create_service_room(client):
    service = client.post("/api/v1/services", json={"name": "Serviço Centro"}).json()
    response = client.post(
        "/api/v1/service-rooms",
        json={
            "service_id": service["id"],
            "name": "Sala 01",
            "room_capacity": 6,
            "has_gurney": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["service_id"] == service["id"]


def test_create_service_schedule(client):
    service = client.post("/api/v1/services", json={"name": "Serviço Sul"}).json()
    room = client.post(
        "/api/v1/service-rooms",
        json={
            "service_id": service["id"],
            "name": "Sala 02",
            "room_capacity": 4,
            "has_gurney": False,
        },
    ).json()
    institute = client.post("/api/v1/education-institutes", json={"name": "FEEVALE"}).json()
    course = client.post(
        "/api/v1/courses",
        json={"edu_institute_id": institute["id"], "name": "Enfermagem", "requires_gurney": False},
    ).json()
    student = client.post(
        "/api/v1/students",
        json={"edu_institute_id": institute["id"], "course_id": course["id"], "status": "PENDING"},
    ).json()

    response = client.post(
        "/api/v1/service-agendas",
        json={
            "service_room_id": room["id"],
            "week_day": "SEG",
            "shift": "MAN",
            "student_id": student["id"],
            "is_active": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["student_id"] == student["id"]


# ── Course ────────────────────────────────────────────────────────────────────

def test_create_course(client):
    inst = client.post("/api/v1/education-institutes", json={"name": "PUCRS"}).json()
    response = client.post(
        "/api/v1/courses",
        json={
            "edu_institute_id": inst["id"],
            "name": "Enfermagem",
            "requires_gurney": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["requires_gurney"] is True


# ── Student ───────────────────────────────────────────────────────────────────

def test_create_student(client):
    inst = client.post("/api/v1/education-institutes", json={"name": "FEEVALE"}).json()
    course = client.post(
        "/api/v1/courses",
        json={"edu_institute_id": inst["id"], "name": "Fisioterapia", "requires_gurney": False},
    ).json()
    response = client.post(
        "/api/v1/students",
        json={"edu_institute_id": inst["id"], "course_id": course["id"], "status": "PENDING"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"
