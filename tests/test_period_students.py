from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.domains.course.model import Course
from app.domains.education_institute.model import EducationInstitute
from app.domains.period.model import Period
from app.domains.period.router import unlink_student_from_period
from app.domains.period.schemas import StudentLinkRequest
from app.domains.room.model import Room
from app.domains.room_schedule import repository_nested as schedule_repository
from app.domains.service.model import Service
from app.domains.student.model import Student
from app.domains.user.model import User

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
    c = TestClient(app)
    try:
        yield c
    finally:
        c.close()
        app.dependency_overrides.clear()


def _create_institute_course_student(client, institute_name="Inst X"):
    inst = client.post("/api/v1/education-institutes", json={"name": institute_name}).json()
    course = client.post(
        "/api/v1/courses",
        json={"edu_institute_id": inst["id"], "name": "Enfermagem", "requires_gurney": False},
    ).json()
    student = client.post(
        "/api/v1/students",
        json={
            "edu_institute_id": inst["id"],
            "course_id": course["id"],
            "status": "PENDING",
            "document_url": "https://example.com/document.pdf",
        },
    ).json()
    return inst, course, student


def _create_priority_period(client):
    today = date.today()
    return client.post(
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


def _make_institute_headers(client, db, institute_id, email="inst@test.com"):
    from app.domains.user.repository import create as create_user
    from app.domains.user.schemas import UserCreate

    create_user(
        db,
        UserCreate(
            name="InstUser",
            email=email,
            password="pass",
            role="education_institute",
            education_institute_id=institute_id,
        ),
    )
    tokens = client.post("/api/v1/auth/login", json={"email": email, "password": "pass"}).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _make_role_headers(client, db, role, email):
    user = User(
        name=role.title(),
        email=email,
        password=hash_password("pass"),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    tokens = client.post("/api/v1/auth/login", json={"email": email, "password": "pass"}).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_link_and_unlink_student_to_period(client, db):
    inst, _course, student = _create_institute_course_student(client)
    period = _create_priority_period(client)
    headers = _make_institute_headers(client, db, inst["id"])

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

    resp_histories = client.get(f"/api/v1/histories/by-period/{period['id']}", headers=headers)
    assert resp_histories.status_code == 200
    histories_body = resp_histories.json()
    assert histories_body["pagination"]["total"] == 1
    assert histories_body["items"][0]["student_id"] == student["id"]
    assert histories_body["items"][0]["period_id"] == period["id"]
    assert histories_body["items"][0]["end_date"] is None

    # unlink student
    resp_unlink = client.request("DELETE", f"/api/v1/periods/{period['id']}/students", json={"student_id": student["id"]}, headers=headers)
    assert resp_unlink.status_code == 200
    assert resp_unlink.json()["message"] == "Aluno desvinculado com sucesso"

    resp_histories_after_unlink = client.get(f"/api/v1/histories/by-period/{period['id']}", headers=headers)
    assert resp_histories_after_unlink.status_code == 200
    histories_after_unlink = resp_histories_after_unlink.json()
    assert histories_after_unlink["pagination"]["total"] == 1
    assert histories_after_unlink["items"][0]["end_date"] is not None

    # unlink again is idempotent
    resp_unlink2 = client.request("DELETE", f"/api/v1/periods/{period['id']}/students", json={"student_id": student["id"]}, headers=headers)
    assert resp_unlink2.status_code == 200
    assert resp_unlink2.json()["message"] == "Aluno desvinculado com sucesso"


def test_admin_can_unlink_student_from_period(client, db):
    inst, _course, student = _create_institute_course_student(client)
    period = _create_priority_period(client)
    institute_headers = _make_institute_headers(client, db, inst["id"])
    admin_headers = _make_role_headers(client, db, "admin", "admin@test.com")

    resp_link = client.post(
        f"/api/v1/periods/{period['id']}/students",
        json={"student_id": student["id"]},
        headers=institute_headers,
    )
    assert resp_link.status_code == 201

    resp_unlink = client.request(
        "DELETE",
        f"/api/v1/periods/{period['id']}/students",
        json={"student_id": student["id"]},
        headers=admin_headers,
    )
    assert resp_unlink.status_code == 200
    assert resp_unlink.json()["message"] == "Aluno desvinculado com sucesso"


def test_service_cannot_unlink_student_from_period(client, db):
    _inst, _course, student = _create_institute_course_student(client)
    period = _create_priority_period(client)
    service_headers = _make_role_headers(client, db, "service", "service@test.com")

    resp = client.request(
        "DELETE",
        f"/api/v1/periods/{period['id']}/students",
        json={"student_id": student["id"]},
        headers=service_headers,
    )
    assert resp.status_code == 403


def test_institute_cannot_unlink_student_from_other_institute(client, db):
    inst, _course, _student = _create_institute_course_student(client, "Inst A")
    _other_inst, _other_course, other_student = _create_institute_course_student(client, "Inst B")
    period = _create_priority_period(client)
    headers = _make_institute_headers(client, db, inst["id"])

    from app.domains.period import repository as period_repository
    from app.domains.student import repository as student_repository

    other_student_model = student_repository.get_by_id(db, other_student["id"])
    period_repository.link_student(db, period["id"], other_student_model)

    resp = client.request(
        "DELETE",
        f"/api/v1/periods/{period['id']}/students",
        json={"student_id": other_student["id"]},
        headers=headers,
    )
    assert resp.status_code == 403


def test_period_unlink_removes_student_from_schedule_slot(db):
    today = date.today()
    institute = EducationInstitute(name="Inst X", priority=0, is_active=True)
    service = Service(name="Service X", is_active=True)
    db.add_all([institute, service])
    db.commit()
    db.refresh(institute)
    db.refresh(service)

    course = Course(name="Enfermagem", requires_gurney=False)
    room = Room(service_id=service.id, name="Sala 1", room_capacity=2, has_gurney=False, is_active=True)
    db.add_all([course, room])
    db.commit()
    db.refresh(course)
    db.refresh(room)
    schedule_repository.create_schedule_for_room(db, room.id)

    student = Student(
        edu_institute_id=institute.id,
        course_id=course.id,
        status="PENDING",
        document_url="https://example.com/document.pdf",
        is_active=True,
    )
    period = Period(
        name="2026.1",
        priority_start_date=today - timedelta(days=1),
        priority_end_date=today + timedelta(days=1),
        start_date=today + timedelta(days=2),
        end_date=today + timedelta(days=30),
        is_active=True,
    )
    db.add_all([student, period])
    db.commit()
    db.refresh(student)
    db.refresh(period)

    assigned_period = schedule_repository.assign_student_to_period(
        db=db,
        room_id=room.id,
        day_of_week="MONDAY",
        period_name="EVENING",
        student_id=student.id,
    )
    assert assigned_period is not None
    assert any(existing.id == student.id for existing in assigned_period.students)

    current_user = User(
        name="Admin",
        email="admin@test.com",
        role="admin",
        is_active=True,
    )
    response = unlink_student_from_period(
        period_id=period.id,
        data=StudentLinkRequest(student_id=student.id),
        db=db,
        current_user=current_user,
    )

    updated_period = schedule_repository.get_period_for_room(db, room.id, "MONDAY", "EVENING")
    assert response["message"] == "Aluno desvinculado com sucesso"
    assert updated_period is not None
    assert all(existing.id != student.id for existing in updated_period.students)


def test_list_histories_by_room(client, db):
    today = date.today()
    institute = EducationInstitute(name="Inst X", priority=0, is_active=True)
    service = Service(name="Service X", is_active=True)
    db.add_all([institute, service])
    db.commit()
    db.refresh(institute)
    db.refresh(service)

    course = Course(name="Enfermagem", requires_gurney=False)
    room = Room(service_id=service.id, name="Sala 1", room_capacity=2, has_gurney=False, is_active=True)
    db.add_all([course, room])
    db.commit()
    db.refresh(course)
    db.refresh(room)
    schedule_repository.create_schedule_for_room(db, room.id)

    student = Student(
        edu_institute_id=institute.id,
        course_id=course.id,
        status="PENDING",
        document_url="https://example.com/document.pdf",
        is_active=True,
    )
    period = Period(
        name="2026.1",
        priority_start_date=today - timedelta(days=1),
        priority_end_date=today + timedelta(days=1),
        start_date=today + timedelta(days=2),
        end_date=today + timedelta(days=30),
        is_active=True,
    )
    db.add_all([student, period])
    db.commit()
    db.refresh(student)
    db.refresh(period)

    assigned_period = schedule_repository.assign_student_to_period(
        db=db,
        room_id=room.id,
        day_of_week="MONDAY",
        period_name="EVENING",
        student_id=student.id,
    )
    assert assigned_period is not None

    from app.domains.period import repository as period_repository

    period_repository.link_student(db, period.id, student)

    admin_headers = _make_role_headers(client, db, "admin", "admin-room@test.com")
    response = client.get(f"/api/v1/histories/by-room/{room.id}", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert body["items"][0]["room_id"] == room.id
    assert body["items"][0]["student_id"] == student.id


def test_list_histories_by_schedule(client, db):
    today = date.today()
    institute = EducationInstitute(name="Inst X", priority=0, is_active=True)
    service = Service(name="Service X", is_active=True)
    db.add_all([institute, service])
    db.commit()
    db.refresh(institute)
    db.refresh(service)

    course = Course(name="Enfermagem", requires_gurney=False)
    room = Room(service_id=service.id, name="Sala 1", room_capacity=2, has_gurney=False, is_active=True)
    db.add_all([course, room])
    db.commit()
    db.refresh(course)
    db.refresh(room)
    schedule_repository.create_schedule_for_room(db, room.id)
    schedule = schedule_repository.get_schedule_by_room(db, room.id)
    assert schedule is not None

    student = Student(
        edu_institute_id=institute.id,
        course_id=course.id,
        status="PENDING",
        document_url="https://example.com/document.pdf",
        is_active=True,
    )
    period = Period(
        name="2026.1",
        priority_start_date=today - timedelta(days=1),
        priority_end_date=today + timedelta(days=1),
        start_date=today + timedelta(days=2),
        end_date=today + timedelta(days=30),
        is_active=True,
    )
    db.add_all([student, period])
    db.commit()
    db.refresh(student)
    db.refresh(period)

    assigned_period = schedule_repository.assign_student_to_period(
        db=db,
        room_id=room.id,
        day_of_week="MONDAY",
        period_name="EVENING",
        student_id=student.id,
    )
    assert assigned_period is not None

    from app.domains.period import repository as period_repository

    period_repository.link_student(db, period.id, student)

    admin_headers = _make_role_headers(client, db, "admin", "admin-schedule@test.com")
    response = client.get(f"/api/v1/histories/by-schedule/{schedule.id}", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert body["items"][0]["schedule_id"] == schedule.id
    assert body["items"][0]["room_id"] == room.id
