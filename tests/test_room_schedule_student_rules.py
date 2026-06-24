from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.domains.history.model import History
from app.domains.period.model import Period, period_students
from app.domains.room_schedule import repository_nested as schedule_repository
from app.domains.student.model import Student

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
    internships = client.post("/api/v1/internshipss", json={"name": "Serviço Teste"}).json()
    institute = client.post("/api/v1/education-institutes", json={"name": "Instituto Teste"}).json()
    discipline = client.post(
        "/api/v1/disciplines",
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
            "discipline_id": discipline["id"],
            "status": "PENDING",
            "document_url": "https://example.com/document.pdf",
        },
    ).json()
    room = client.post(
        "/api/v1/rooms",
        json={
            "internship_id": internships["id"],
            "name": "Sala 01",
            "room_capacity": 10,
            "has_gurney": has_gurney,
        },
    ).json()
    return internships, institute, discipline, student, room

def _create_period(db):
    today = date.today()
    period = Period(
        name="2026.1",
        priority_start_date=today,
        priority_end_date=today,
        start_date=today,
        end_date=today,
        is_active=True,
    )
    db.add(period)
    db.commit()
    db.refresh(period)
    return period

def test_prevents_student_conflict_in_other_room(client, db):
    internships, _institute, _discipline, student, room1 = _create_basic_entities(client)
    period = _create_period(db)
    room2 = client.post(
        "/api/v1/rooms",
        json={
            "internship_id": internships["id"],
            "name": "Sala 02",
            "room_capacity": 10,
            "has_gurney": True,
        },
    ).json()

    resp_ok = client.post(
        "/api/v1/rooms/schedule/student",
        json={
            "room_id": room1["id"],
            "day_of_week": "MONDAY",
            "period": "MORNING",
            "period_id": period.id,
            "student_id": student["id"],
        },
    )
    assert resp_ok.status_code == 200

    resp_conflict = client.post(
        "/api/v1/rooms/schedule/student",
        json={
            "room_id": room2["id"],
            "day_of_week": "MONDAY",
            "period": "MORNING",
            "period_id": period.id,
            "student_id": student["id"],
        },
    )
    assert resp_conflict.status_code == 409
    assert "outra sala" in resp_conflict.json()["detail"].lower()

def test_requires_gurney_when_discipline_needs_it(client, db):
    _, _institute, _discipline, student, room = _create_basic_entities(client, requires_gurney=True, has_gurney=False)
    period = _create_period(db)

    resp = client.post(
        "/api/v1/rooms/schedule/student",
        json={
            "room_id": room["id"],
            "day_of_week": "MONDAY",
            "period": "MORNING",
            "period_id": period.id,
            "student_id": student["id"],
        },
    )
    assert resp.status_code == 409
    assert "maca" in resp.json()["detail"].lower()

def test_room_schedule_link_updates_history_and_unlink_closes_it(client, db):
    _internships, _institute, _discipline, student, room = _create_basic_entities(client)

    schedule_repository.create_schedule_for_room(db, room["id"])

    period = _create_period(db)
    student_model = db.query(Student).filter(Student.id == student["id"]).first()
    assert student_model is not None

    db.execute(period_students.insert().values(period_id=period.id, student_id=student_model.id))
    db.commit()

    history_before = db.query(History).filter(
        History.period_id == period.id,
        History.student_id == student_model.id,
    ).all()
    assert len(history_before) == 0

    response_link = client.post(
        "/api/v1/rooms/schedule/student",
        json={
            "room_id": room["id"],
            "day_of_week": "MONDAY",
            "period": "MORNING",
            "period_id": period.id,
            "student_id": student_model.id,
        },
    )
    assert response_link.status_code == 200

    schedule_model = schedule_repository.get_schedule_by_room(db, room["id"])
    assert schedule_model is not None

    history_after_link = db.query(History).filter(
        History.period_id == period.id,
        History.student_id == student_model.id,
    ).all()
    assert len(history_after_link) == 1
    assert history_after_link[0].room_id == room["id"]
    assert history_after_link[0].schedule_id == schedule_model.id
    assert history_after_link[0].start_date == date.today()
    assert history_after_link[0].end_date is None

    response_unlink = client.request(
        "DELETE",
        "/api/v1/rooms/schedule/student",
        json={
            "room_id": room["id"],
            "day_of_week": "MONDAY",
            "period": "MORNING",
            "period_id": period.id,
            "student_id": student_model.id,
        },
    )
    assert response_unlink.status_code == 200

    history_after_unlink = db.query(History).filter(
        History.period_id == period.id,
        History.student_id == student_model.id,
    ).all()
    assert len(history_after_unlink) == 1
    assert history_after_unlink[0].end_date == date.today()

def test_get_room_schedule_receives_room_id_in_body(client):
    _internships, _institute, _discipline, _student, room = _create_basic_entities(client)

    response = client.post(
        "/api/v1/rooms/schedule",
        json={"room_id": room["id"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["roomId"] == room["id"]
    assert len(body["days"]) == 7

def test_available_slots_receives_filters_in_body(client):
    _internships, _institute, _discipline, student, room = _create_basic_entities(client)

    response = client.post(
        "/api/v1/rooms/available-slots",
        json={
            "student_id": student["id"],
            "room_id": room["id"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0
    assert body[0]["room_id"] == room["id"]
