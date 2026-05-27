from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_periods.db"
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

from app.core.database import get_db


def test_link_and_unlink_student_to_period(client, db):
    # create institute, course, student
    inst = client.post("/api/v1/education-institutes", json={"name": "Inst X"}).json()
    course = client.post(
        "/api/v1/courses",
        json={"edu_institute_id": inst["id"], "name": "Enfermagem", "requires_gurney": False},
    ).json()
    student = client.post(
        "/api/v1/students",
        json={"edu_institute_id": inst["id"], "course_id": course["id"], "status": "PENDING"},
    ).json()

    # create period where today is within priority window
    today = date.today()
    period = client.post(
        "/api/v1/periods",
        json={
            "name": "2026.1",
            "priority_start_date": (today - timedelta(days=1)).isoformat(),
            "priority_end_date": (today + timedelta(days=1)).isoformat(),
            "start_date": (today + timedelta(days=2)).isoformat(),
            "end_date": (today + timedelta(days=30)).isoformat(),
            "is_active": True,
        },
    ).json()

    # create institute user directly in DB and login
    from app.domains.user.repository import create as create_user
    from app.domains.user.schemas import UserCreate

    create_user(db, UserCreate(name="InstUser", email="inst@test.com", password="pass", role="education_institute", education_institute_id=inst["id"]))
    tokens = client.post("/api/v1/auth/login", json={"email": "inst@test.com", "password": "pass"}).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # link student
    resp = client.post(f"/api/v1/periods/{period['id']}/students", json={"student_id": student["id"]}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["message"] == "Aluno vinculado com sucesso"

    # linking again should return conflict
    resp_dup = client.post(f"/api/v1/periods/{period['id']}/students", json={"student_id": student["id"]}, headers=headers)
    assert resp_dup.status_code == 409

    # get period with students
    resp_get = client.get(f"/api/v1/periods/{period['id']}?include=students", headers=headers)
    assert resp_get.status_code == 200
    body = resp_get.json()
    assert "students" in body
    assert any(s["id"] == student["id"] for s in body["students"])

    # unlink student
    resp_unlink = client.request("DELETE", f"/api/v1/periods/{period['id']}/students", json={"student_id": student["id"]}, headers=headers)
    assert resp_unlink.status_code == 200
    assert resp_unlink.json()["message"] == "Aluno desvinculado com sucesso"

    # unlink again should return 404
    resp_unlink2 = client.request("DELETE", f"/api/v1/periods/{period['id']}/students", json={"student_id": student["id"]}, headers=headers)
    assert resp_unlink2.status_code == 404
