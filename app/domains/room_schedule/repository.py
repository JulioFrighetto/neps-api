from sqlalchemy.orm import Session

from app.domains.room.model import Room
from app.domains.room_schedule.model import RoomSchedule, RoomScheduleStudent


WEEK_DAYS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
SHIFTS = ["manhã", "tarde", "noite"]


def create_schedule_for_room(db: Session, room_id: int) -> list[RoomSchedule]:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        return []
    schedules = []
    for day in WEEK_DAYS:
        for shift in SHIFTS:
            schedule = RoomSchedule(
                room_id=room_id,
                week_day=day,
                shift=shift,
                capacity=room.room_capacity,
            )
            schedules.append(schedule)
    db.add_all(schedules)
    db.commit()
    for schedule in schedules:
        db.refresh(schedule)
    return schedules


def get_by_room(db: Session, room_id: int) -> list[RoomSchedule]:
    return db.query(RoomSchedule).filter(RoomSchedule.room_id == room_id).all()


def add_student_to_schedule(db: Session, schedule_id: int, student_id: int) -> RoomScheduleStudent | None:
    schedule = db.query(RoomSchedule).filter(RoomSchedule.id == schedule_id).first()
    if not schedule:
        return None
    current_count = len(schedule.students)
    if current_count >= schedule.capacity:
        return None
    link = RoomScheduleStudent(room_schedule_id=schedule_id, student_id=student_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def remove_student_from_schedule(db: Session, schedule_id: int, student_id: int) -> bool:
    link = db.query(RoomScheduleStudent).filter(
        RoomScheduleStudent.room_schedule_id == schedule_id,
        RoomScheduleStudent.student_id == student_id,
    ).first()
    if not link:
        return False
    db.delete(link)
    db.commit()
    return True