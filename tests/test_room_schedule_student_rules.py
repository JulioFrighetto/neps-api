import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_room_schedule_student_rules.db"
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


def _create_basic_entities(client, *, requires_gurney: bool = False, has_gurney: bool = True):
    service = client.post("/api/v1/services", json={"name": "Serviço Teste"}).json()
    institute = client.post("/api/v1/education-institutes", json={"name": "Instituto Teste"}).json()
    course = client.post(
        "/api/v1/courses",
        json={
            "edu_institute_id": institute["id"],
            "name": "Curso Teste",
            "requires_gurney": requires_gurney,
        },
    ).json()
    student = client.post(
        "/api/v1/students",
        json={
            "edu_institute_id": institute["id"],
            "course_id": course["id"],
            "status": "PENDING",
        },
    ).json()
    room = client.post(
        "/api/v1/rooms",
        json={
            "service_id": service["id"],
            "name": "Sala 01",
            "room_capacity": 10,
            "has_gurney": has_gurney,
        },
    ).json()
    return service, institute, course, student, room


def test_prevents_student_conflict_in_other_room(client):
    service, institute, course, student, room1 = _create_basic_entities(client)
    room2 = client.post(
        "/api/v1/rooms",
        json={
            "service_id": service["id"],
            "name": "Sala 02",
            "room_capacity": 10,
            "has_gurney": True,
        },
    ).json()

    resp_ok = client.post(
        f"/api/v1/rooms/{room1['id']}/schedule/MONDAY/MORNING/student",
        json={"student_id": student["id"]},
    )
    assert resp_ok.status_code == 200

    resp_conflict = client.post(
        f"/api/v1/rooms/{room2['id']}/schedule/MONDAY/MORNING/student",
        json={"student_id": student["id"]},
    )
    assert resp_conflict.status_code == 409
    assert "outra sala" in resp_conflict.json()["detail"].lower()


def test_requires_gurney_when_course_needs_it(client):
    _, _, _, student, room = _create_basic_entities(client, requires_gurney=True, has_gurney=False)

    resp = client.post(
        f"/api/v1/rooms/{room['id']}/schedule/MONDAY/MORNING/student",
        json={"student_id": student["id"]},
    )
    assert resp.status_code == 409
    assert "maca" in resp.json()["detail"].lower()
