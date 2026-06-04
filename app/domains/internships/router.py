import math

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo

from app.domains.internships.usecases.list_usecase import list_internships_usecase
from app.domains.internships.usecases.get_usecase import get_internship_usecase
from app.domains.internships.usecases.create_usecase import create_internship_usecase
from app.domains.internships.usecases.update_usecase import update_internship_usecase
from app.domains.internships.usecases.replace_usecase import replace_internship_usecase
from app.domains.internships.schemas import InternshipsCreate, InternshipsResponse, InternshipsUpdate
from pydantic import BaseModel

router = APIRouter(prefix="/internships", tags=["Internships"])

AVAILABLE_FILTERS = ["name_like", "region_id", "is_active"]


from pydantic import BaseModel, Field

class InternshipsGetRequest(BaseModel):
    internship_id: int = Field(..., alias="internship_id")
    # Compatibilidade com use‑case que espera `internships_id`
    @property
    def internships_id(self) -> int:
        return self.internship_id


class InternshipsUpdateRequest(InternshipsUpdate):
    internships_id: int


class InternshipsReplaceRequest(InternshipsCreate):
    internship_id: int = Field(..., alias="internship_id")
    @property
    def internships_id(self) -> int:
        return self.internship_id


@router.get("/", response_model=Page[InternshipsResponse])
def list_internships(
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    name_like: str | None = Body(None),
    region_id: int | None = Body(None),
    is_active: bool | None = Body(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {k: v for k, v in {"name_like": name_like, "region_id": region_id, "is_active": is_active}.items() if v is not None}
    items, total = list_internships_usecase(db, page, per_page, filters, current_user)
    return Page(
        items=items,
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
        filters=FilterInfo(applied=list(filters.keys()), available=AVAILABLE_FILTERS),
    )


@router.post("/detail", response_model=InternshipsResponse)
def get_internship(data: InternshipsGetRequest, db: Session = Depends(get_db)):
    return get_internship_usecase(db, data.internships_id)


@router.post("/", response_model=InternshipsResponse, status_code=status.HTTP_201_CREATED)
def create_internship(data: InternshipsCreate, db: Session = Depends(get_db)):
    return create_internship_usecase(db, data)


@router.patch("/", response_model=InternshipsResponse)
def update_internship(data: InternshipsUpdateRequest, db: Session = Depends(get_db)):
    return update_internship_usecase(db, data)


@router.put("/", response_model=InternshipsResponse)
def replace_internship(data: InternshipsReplaceRequest, db: Session = Depends(get_db)):
    return update_internship_usecase(db, data)
