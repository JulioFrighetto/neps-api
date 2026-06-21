import math

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.internships.schemas import (InternshipsCreate,
                                             InternshipsResponse,
                                             InternshipsUpdate)
from app.domains.internships.usecases.create_usecase import \
    create_internship_usecase
from app.domains.internships.usecases.get_usecase import get_internship_usecase
from app.domains.internships.usecases.list_usecase import \
    list_internships_usecase
from app.domains.internships.usecases.replace_usecase import \
    replace_internship_usecase
from app.domains.internships.usecases.update_usecase import \
    update_internship_usecase

router = APIRouter(prefix="/internships", tags=["Internships"])

AVAILABLE_FILTERS = ["name_like", "region_id", "is_active"]


from pydantic import BaseModel, ConfigDict, Field


class InternshipsGetRequest(BaseModel):
    internship_id: int = Field(..., alias="internship_id")
    # Compatibilidade com use‑case que espera `internship_id`
    @property
    def internship_id(self) -> int:
        return self.internship_id


class InternshipsUpdateRequest(InternshipsUpdate):
    internship_id: int


class InternshipsReplaceRequest(InternshipsCreate):
    internship_id: int = Field(..., alias="internship_id")
    @property
    def internship_id(self) -> int:
        return self.internship_id


@router.get("/", response_model=Page[InternshipsResponse])
def list_internships(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Itens por página"),
    name_like: str | None = Query(None, description="Filtro por nome"),
    region_id: int | None = Query(None, description="Filtro por Território"),
    is_active: bool | None = Query(None, description="Filtro por status ativo"),
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
    return get_internship_usecase(db, data.internship_id)


class ByRegionRequest(BaseModel):
    region_id: int


class InternshipBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    region_id: int | None = None
    is_active: bool


class ByRegionResponse(BaseModel):
    items: list[InternshipBrief]


@router.post("/by-region", response_model=ByRegionResponse)
def list_internships_by_region(
    data: ByRegionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    from app.domains.internships.model import Internship
    items = (
        db.query(Internship)
        .filter(Internship.region_id == data.region_id, Internship.is_active.is_(True))
        .all()
    )
    return ByRegionResponse(items=items)


@router.post("/", response_model=InternshipsResponse, status_code=status.HTTP_201_CREATED)
def create_internship(data: InternshipsCreate, db: Session = Depends(get_db)):
    return create_internship_usecase(db, data)


@router.patch("/", response_model=InternshipsResponse)
def update_internship(data: InternshipsUpdateRequest, db: Session = Depends(get_db)):
    return update_internship_usecase(db, data)


@router.put("/", response_model=InternshipsResponse)
def replace_internship(data: InternshipsReplaceRequest, db: Session = Depends(get_db)):
    return update_internship_usecase(db, data)
