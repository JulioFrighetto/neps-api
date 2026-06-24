from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.domains.education_institute.model import EducationInstitute
from app.domains.internships.model import Internship
from app.domains.internships_room.model import InternshipsRoom
from app.domains.period.model import Period
from app.domains.region.model import Region
from app.domains.room.model import Room
from app.domains.room_schedule.models_nested import Schedule, ScheduleDay, SchedulePeriod, schedule_period_students
from app.domains.student.model import Student

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

class DashboardResponse(BaseModel):
    total_students: int
    total_internships: int
    total_periods: int
    total_institutions: int
    total_rooms: int

@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student_query = db.query(func.count(Student.id))
    if current_user.role == "education_institute" and current_user.education_institute_id:
        student_query = student_query.filter(Student.edu_institute_id == current_user.education_institute_id)

    total_students = student_query.scalar() or 0
    total_internships = db.query(func.count(Internship.id)).scalar() or 0
    total_periods = db.query(func.count(Period.id)).scalar() or 0
    total_institutions = db.query(func.count(EducationInstitute.id)).scalar() or 0
    total_rooms = db.query(func.count(InternshipsRoom.id)).scalar() or 0

    return DashboardResponse(
        total_students=total_students,
        total_internships=total_internships,
        total_periods=total_periods,
        total_institutions=total_institutions,
        total_rooms=total_rooms,
    )

class RegionSlotItem(BaseModel):
    region_id: int
    region_name: str
    vacancies: int

class RegionSlotResponse(BaseModel):
    items: list[RegionSlotItem]

@router.get("/vacancies-by-region", response_model=RegionSlotResponse)
def vacancies_by_region(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = (
        db.query(Region.id, Region.name, func.sum(Room.room_capacity).label("vacancies"))
        .join(Internship, Internship.region_id == Region.id)
        .join(Room, Room.internship_id == Internship.id)
        .filter(Room.is_active.is_(True), Internship.is_active.is_(True))
        .group_by(Region.id, Region.name)
        .order_by(func.sum(Room.room_capacity).desc())
        .all()
    )
    return RegionSlotResponse(
        items=[
            RegionSlotItem(region_id=r.id, region_name=r.name, vacancies=r.vacancies)
            for r in rows
        ]
    )

class StudentsByInstitutionItem(BaseModel):
    institution_id: int
    institution_name: str
    student_count: int

class StudentsByInstitutionResponse(BaseModel):
    items: list[StudentsByInstitutionItem]

@router.get("/students-by-institution", response_model=StudentsByInstitutionResponse)
def students_by_institution(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = (
        db.query(
            EducationInstitute.id,
            EducationInstitute.name,
            func.count(Student.id).label("student_count"),
        )
        .join(Student, Student.edu_institute_id == EducationInstitute.id)
        .filter(Student.internship_id.isnot(None))
    )
    if current_user.role == "education_institute" and current_user.education_institute_id:
        query = query.filter(EducationInstitute.id == current_user.education_institute_id)

    rows = query.group_by(EducationInstitute.id, EducationInstitute.name).order_by(func.count(Student.id).desc()).all()
    return StudentsByInstitutionResponse(
        items=[
            StudentsByInstitutionItem(institution_id=r.id, institution_name=r.name, student_count=r.student_count)
            for r in rows
        ]
    )

class InstitutionCount(BaseModel):
    institution_name: str
    student_count: int

class StudentsByRegionInstitutionItem(BaseModel):
    region_name: str
    institutions: list[InstitutionCount]

class StudentsByRegionInstitutionResponse(BaseModel):
    items: list[StudentsByRegionInstitutionItem]

@router.get("/students-by-region-institution", response_model=StudentsByRegionInstitutionResponse)
def students_by_region_institution(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = (
        db.query(
            Region.name.label("region_name"),
            EducationInstitute.name.label("institution_name"),
            func.count(Student.id).label("student_count"),
        )
        .join(Internship, Student.internship_id == Internship.id)
        .join(Region, Internship.region_id == Region.id)
        .join(EducationInstitute, Student.edu_institute_id == EducationInstitute.id)
        .filter(Student.internship_id.isnot(None))
    )
    if current_user.role == "education_institute" and current_user.education_institute_id:
        query = query.filter(EducationInstitute.id == current_user.education_institute_id)

    rows = (
        query
        .group_by(Region.id, Region.name, EducationInstitute.id, EducationInstitute.name)
        .order_by(Region.name, func.count(Student.id).desc())
        .all()
    )

    grouped: dict[str, list[InstitutionCount]] = {}
    for r in rows:
        grouped.setdefault(r.region_name, []).append(
            InstitutionCount(institution_name=r.institution_name, student_count=r.student_count)
        )

    return StudentsByRegionInstitutionResponse(
        items=[
            StudentsByRegionInstitutionItem(region_name=region, institutions=institutions)
            for region, institutions in grouped.items()
        ]
    )

class OccupiedByInternshipItem(BaseModel):
    internship_id: int
    internship_name: str
    occupied: int

class OccupiedByInternshipResponse(BaseModel):
    items: list[OccupiedByInternshipItem]

class InternshipCapacityItem(BaseModel):
    internship_id: int
    internship_name: str
    total: int
    occupied: int
    free: int

class InternshipCapacityResponse(BaseModel):
    items: list[InternshipCapacityItem]

@router.get("/capacity-by-internship", response_model=InternshipCapacityResponse)
def capacity_by_internship(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    capacity_query = (
        db.query(
            Internship.id,
            Internship.name,
            func.coalesce(func.sum(Room.room_capacity), 0).label("total"),
        )
        .outerjoin(Room, (Room.internship_id == Internship.id) & Room.is_active.is_(True))
        .filter(Internship.is_active.is_(True))
    )
    if current_user.role == "internships" and current_user.internship_id:
        capacity_query = capacity_query.filter(Internship.id == current_user.internship_id)

    capacity_rows = capacity_query.group_by(Internship.id, Internship.name).all()
    capacity_map = {r.id: (r.name, r.total) for r in capacity_rows}

    occupied_query = (
        db.query(
            Internship.id,
            func.count(schedule_period_students.c.student_id).label("occupied"),
        )
        .join(Room, Room.internship_id == Internship.id)
        .join(Schedule, Schedule.room_id == Room.id)
        .join(ScheduleDay, ScheduleDay.schedule_id == Schedule.id)
        .join(SchedulePeriod, SchedulePeriod.schedule_day_id == ScheduleDay.id)
        .join(schedule_period_students, schedule_period_students.c.schedule_period_id == SchedulePeriod.id)
        .filter(Room.is_active.is_(True), Internship.is_active.is_(True))
    )
    if current_user.role == "internships" and current_user.internship_id:
        occupied_query = occupied_query.filter(Internship.id == current_user.internship_id)

    occupied_map = {r.id: r.occupied for r in occupied_query.group_by(Internship.id).all()}

    items = []
    for internship_id, (name, total) in capacity_map.items():
        occupied = occupied_map.get(internship_id, 0)
        items.append(InternshipCapacityItem(
            internship_id=internship_id,
            internship_name=name,
            total=total,
            occupied=occupied,
            free=max(0, total - occupied),
        ))

    items.sort(key=lambda x: x.total, reverse=True)
    return InternshipCapacityResponse(items=items)

@router.get("/occupied-by-internship", response_model=OccupiedByInternshipResponse)
def occupied_by_internship(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = (
        db.query(
            Internship.id,
            Internship.name,
            func.count(schedule_period_students.c.student_id).label("occupied"),
        )
        .join(Room, Room.internship_id == Internship.id)
        .join(Schedule, Schedule.room_id == Room.id)
        .join(ScheduleDay, ScheduleDay.schedule_id == Schedule.id)
        .join(SchedulePeriod, SchedulePeriod.schedule_day_id == ScheduleDay.id)
        .join(schedule_period_students, schedule_period_students.c.schedule_period_id == SchedulePeriod.id)
        .filter(Room.is_active.is_(True), Internship.is_active.is_(True))
    )
    if current_user.role == "internships" and current_user.internship_id:
        query = query.filter(Internship.id == current_user.internship_id)

    rows = (
        query
        .group_by(Internship.id, Internship.name)
        .order_by(func.count(schedule_period_students.c.student_id).desc())
        .all()
    )
    return OccupiedByInternshipResponse(
        items=[
            OccupiedByInternshipItem(internship_id=r.id, internship_name=r.name, occupied=r.occupied)
            for r in rows
        ]
    )

@router.get("/occupied-by-region", response_model=RegionSlotResponse)
def occupied_by_region(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = (
        db.query(Region.id, Region.name, func.count(schedule_period_students.c.student_id).label("vacancies"))
        .join(Internship, Internship.region_id == Region.id)
        .join(Room, Room.internship_id == Internship.id)
        .join(Schedule, Schedule.room_id == Room.id)
        .join(ScheduleDay, ScheduleDay.schedule_id == Schedule.id)
        .join(SchedulePeriod, SchedulePeriod.schedule_day_id == ScheduleDay.id)
        .join(schedule_period_students, schedule_period_students.c.schedule_period_id == SchedulePeriod.id)
        .filter(Room.is_active.is_(True), Internship.is_active.is_(True))
        .group_by(Region.id, Region.name)
        .order_by(func.count(schedule_period_students.c.student_id).desc())
        .all()
    )
    return RegionSlotResponse(
        items=[
            RegionSlotItem(region_id=r.id, region_name=r.name, vacancies=r.vacancies)
            for r in rows
        ]
    )
