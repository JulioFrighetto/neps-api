from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

class PaginationInfo(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int

class FilterInfo(BaseModel):
    applied: list[str]
    available: list[str] = []

class Page(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationInfo
    filters: FilterInfo | None = None
