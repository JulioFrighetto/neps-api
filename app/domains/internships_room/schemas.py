from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InternshipsRoomBase(BaseModel):
    internships_id: int
    name: str
    room_capacity: int
    has_gurney: bool = False
    is_active: bool = True


class InternshipsRoomCreate(InternshipsRoomBase):
    pass


class InternshipsRoomUpdate(BaseModel):
    name: str | None = None
    room_capacity: int | None = None
    has_gurney: bool | None = None
    is_active: bool | None = None


class InternshipsRoomResponse(InternshipsRoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
