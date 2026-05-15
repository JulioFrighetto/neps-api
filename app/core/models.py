# Import all models here so SQLAlchemy's metadata is fully populated
# before create_all() is called.
from app.domains.education_institution.model import EducationInstitution  # noqa: F401
from app.domains.course.model import Course  # noqa: F401
from app.domains.internship_field.model import InternshipField, Region  # noqa: F401
from app.domains.room.model import Room, RoomSchedule, RoomTimeTable, TimeTableStudent  # noqa: F401
from app.domains.student.model import Student  # noqa: F401
from app.domains.internship.model import Internship, InternshipRecord, InternshipDocument  # noqa: F401
from app.domains.user.model import User  # noqa: F401
