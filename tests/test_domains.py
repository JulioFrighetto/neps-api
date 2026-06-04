from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.core.models import *  # noqa: F401, F403
from app.main import app
from app.domains.education_institute.model import EducationInstitute
from app.domains.internships.model import Internships
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


def _make_admin_token(client):
    """Seed an admin user and return a valid access token."""
    db = next(app.dependency_overrides[get_db]())
    admin = User(
        name="Admin",
        email="admin@test.com",
        password=hash_password("secret123"),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    resp = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "secret123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _make_institute_token(client, db, *, priority: int = 0, email: str = "inst@test.com", password: str = "secret123"):
    institute = EducationInstitute(name="Instituição Teste", priority=priority, is_active=True)
    db.add(institute)
    db.commit()
    db.refresh(institute)

    user = User(
        name="Instituição Teste",
        email=email,
        password=hash_password(password),
        role="education_institute",
        education_institute_id=institute.id,
        is_active=True,
    )
    db.add(user)
    db.commit()

    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_list_education_institutes_pagination(client):
    token = _make_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/v1/education-institutes/", json={"name": "UNISINOS"}, headers=headers)
    response = client.get("/api/v1/education-institutes/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


# ── Room ──────────────────────────────────────────────────────────────────────




# ── Internshipss ────────────────────────────────────────────────────────────────

def test_create_internships(client):
    response = client.post(
        "/api/v1/internshipss",
        json={
            "name": "Serviço Norte",
            "is_active": True,
            "user_name": "Internships Norte",
            "user_email": "internships-norte@neps.com",
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Serviço Norte"


def test_create_internships_creates_user(client, db, monkeypatch):
    monkeypatch.setattr("app.domains.internships.router.send_email", lambda *args, **kwargs: None)

    response = client.post(
        "/api/v1/internshipss",
        json={
            "name": "Serviço Centro",
            "is_active": True,
            "user_name": "Internships Centro",
            "user_email": "internships-centro@neps.com",
        },
    )

    assert response.status_code == 201
    internships = db.query(Internships).filter(Internships.name == "Serviço Centro").first()
    assert internships is not None
    user = db.query(User).filter(User.internships_id == internships.id).first()
    assert user is not None
    assert user.role == "internships"
    assert user.email == "internships-centro@neps.com"


def test_create_internships_room(client):
    internships = client.post("/api/v1/internshipss", json={"name": "Serviço Centro"}).json()
    response = client.post(
        "/api/v1/internships-rooms",
        json={
            "internships_id": internships["id"],
            "name": "Sala 01",
            "room_capacity": 6,
            "has_gurney": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["internships_id"] == internships["id"]


def test_create_internships_schedule(client):
    internships = client.post("/api/v1/internshipss", json={"name": "Serviço Sul"}).json()
    room = client.post(
        "/api/v1/internships-rooms",
        json={
            "internships_id": internships["id"],
            "name": "Sala 02",
            "room_capacity": 4,
            "has_gurney": False,
        },
    ).json()
    institute = client.post("/api/v1/education-institutes", json={"name": "FEEVALE"}).json()
    discipline = client.post(
        "/api/v1/disciplines",
        json={"edu_institute_id": institute["id"], "name": "Enfermagem", "requires_gurney": False},
    ).json()
    student = client.post(
        "/api/v1/students",
        json={"edu_institute_id": institute["id"], "discipline_id": discipline["id"], "status": "PENDING"},
    ).json()

    response = client.post(
        "/api/v1/internships-agendas",
        json={
            "internships_room_id": room["id"],
            "week_day": "SEG",
            "shift": "MAN",
            "student_id": student["id"],
            "is_active": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["student_id"] == student["id"]


# ── Discipline ────────────────────────────────────────────────────────────────────

def test_create_discipline(client):
    inst = client.post("/api/v1/education-institutes", json={"name": "PUCRS"}).json()
    response = client.post(
        "/api/v1/disciplines",
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
    discipline = client.post(
        "/api/v1/disciplines",
        json={"edu_institute_id": inst["id"], "name": "Fisioterapia", "requires_gurney": False},
    ).json()
    response = client.post(
        "/api/v1/students",
        json={"edu_institute_id": inst["id"], "discipline_id": discipline["id"], "status": "PENDING"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"


def test_get_student_returns_discipline_and_institution(client):
    inst = client.post("/api/v1/education-institutes", json={"name": "FEEVALE"}).json()
    discipline = client.post(
        "/api/v1/disciplines",
        json={"edu_institute_id": inst["id"], "name": "Fisioterapia", "requires_gurney": False},
    ).json()
    student = client.post(
        "/api/v1/students",
        json={
            "edu_institute_id": inst["id"],
            "discipline_id": discipline["id"],
            "status": "PENDING",
            "document_url": "https://example.com/document.pdf",
        },
    ).json()

    response = client.post("/api/v1/students/detail", json={"student_id": student["id"]})
    assert response.status_code == 200
    body = response.json()
    assert body["discipline"] is not None
    assert body["discipline"]["id"] == discipline["id"]
    assert body["discipline"]["name"] == discipline["name"]
    assert body["institution"] is not None
    assert body["institution"]["id"] == inst["id"]
    assert body["institution"]["name"] == inst["name"]


# ── Filter Tests ─────────────────────────────────────────────────────────────

def test_disciplines_filter_name_like(client):
    client.post("/api/v1/disciplines", json={"name": "Enfermagem", "requires_gurney": True})
    client.post("/api/v1/disciplines", json={"name": "Fisioterapia", "requires_gurney": False})
    client.post("/api/v1/disciplines", json={"name": "Medicina", "requires_gurney": False})

    response = client.get("/api/v1/disciplines?name_like=enfer")
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert body["items"][0]["name"] == "Enfermagem"
    assert "name_like" in body["filters"]["applied"]


def test_disciplines_pagination_page_per_page(client):
    for i in range(5):
        client.post("/api/v1/disciplines", json={"name": f"Curso {i}", "requires_gurney": False})

    response = client.get("/api/v1/disciplines?page=1&per_page=2")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["per_page"] == 2
    assert body["pagination"]["total"] == 5
    assert body["pagination"]["total_pages"] == 3


def test_regions_filter_is_active(client):
    client.post("/api/v1/regions", json={"name": "Norte", "is_active": True})
    client.post("/api/v1/regions", json={"name": "Sul", "is_active": False})

    response = client.get("/api/v1/regions?is_active=true")
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert body["items"][0]["name"] == "Norte"

    response = client.get("/api/v1/regions?is_active=false")
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert body["items"][0]["name"] == "Sul"


def test_regions_filter_name_like(client):
    client.post("/api/v1/regions", json={"name": "Norte", "is_active": True})
    client.post("/api/v1/regions", json={"name": "Nordeste", "is_active": True})
    client.post("/api/v1/regions", json={"name": "Sul", "is_active": True})

    response = client.get("/api/v1/regions?name_like=no")
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 2


def test_periods_filter_date_range(client):
    client.post("/api/v1/periods", json={
        "name": "2025.1",
        "priority_start_date": "2025-01-01",
        "priority_end_date": "2025-01-15",
        "start_date": "2025-02-01",
        "end_date": "2025-06-30",
        "is_active": True,
    })
    client.post("/api/v1/periods", json={
        "name": "2025.2",
        "priority_start_date": "2025-07-01",
        "priority_end_date": "2025-07-15",
        "start_date": "2025-08-01",
        "end_date": "2025-12-31",
        "is_active": True,
    })

    response = client.get("/api/v1/periods?start_date_from=2025-01-01&start_date_to=2025-06-30")
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert "start_date_from" in body["filters"]["applied"]
    assert "start_date_to" in body["filters"]["applied"]

    response = client.get("/api/v1/periods?name_like=2025.2")
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1


def test_periods_list_for_priority_institute_shows_priority_and_open_periods(client, db, monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 5, 27)

    monkeypatch.setattr("app.domains.period.repository.date", FixedDate)

    token = _make_institute_token(client, db, priority=0, email="prio@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/periods",
        json={
            "name": "Prioritário",
            "priority_start_date": "2026-05-20",
            "priority_end_date": "2026-05-30",
            "start_date": "2026-06-01",
            "end_date": "2026-12-31",
            "is_active": True,
        },
    )
    client.post(
        "/api/v1/periods",
        json={
            "name": "Aberto",
            "priority_start_date": "2026-04-01",
            "priority_end_date": "2026-04-10",
            "start_date": "2026-05-01",
            "end_date": "2026-06-30",
            "is_active": True,
        },
    )
    client.post(
        "/api/v1/periods",
        json={
            "name": "Inativo",
            "priority_start_date": "2026-05-20",
            "priority_end_date": "2026-05-30",
            "start_date": "2026-05-01",
            "end_date": "2026-06-30",
            "is_active": False,
        },
    )

    response = client.get("/api/v1/periods", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 2
    names = {item["name"] for item in body["items"]}
    assert names == {"Prioritário", "Aberto"}


def test_periods_list_for_non_priority_institute_shows_only_open_periods(client, db, monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 5, 27)

    monkeypatch.setattr("app.domains.period.repository.date", FixedDate)

    token = _make_institute_token(client, db, priority=1, email="nonprio@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/periods",
        json={
            "name": "Prioritário",
            "priority_start_date": "2026-05-20",
            "priority_end_date": "2026-05-30",
            "start_date": "2026-06-01",
            "end_date": "2026-12-31",
            "is_active": True,
        },
    )
    client.post(
        "/api/v1/periods",
        json={
            "name": "Aberto",
            "priority_start_date": "2026-04-01",
            "priority_end_date": "2026-04-10",
            "start_date": "2026-05-01",
            "end_date": "2026-06-30",
            "is_active": True,
        },
    )

    response = client.get("/api/v1/periods", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert body["items"][0]["name"] == "Aberto"


def test_users_roles_endpoint(client):
    response = client.get("/api/v1/users/roles")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    roles = {item["value"] for item in body["items"]}
    assert "admin" in roles
    assert "education_institute" in roles
    assert "internships" in roles
