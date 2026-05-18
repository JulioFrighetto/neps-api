from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoomBase(BaseModel):
    service_id: int
    name: str
    room_capacity: int
    has_gurney: bool = False
    is_active: bool = True


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: str | None = None
    room_capacity: int | None = None
    has_gurney: bool | None = None
    is_active: bool | None = None


class RoomResponse(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
