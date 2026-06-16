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
    total_students = db.query(func.count(Student.id)).scalar() or 0
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
