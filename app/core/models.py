# Import all models here so SQLAlchemy's metadata is fully populated
# before create_all() is called.
from app.domains.education_institute.model import EducationInstitute  # noqa: F401
from app.domains.student.model import Student  # noqa: F401
from app.domains.course.model import Course  # noqa: F401
from app.domains.internship_field.model import InternshipField  # noqa: F401
from app.domains.region.model import Region  # noqa: F401
from app.domains.room.model import Room  # noqa: F401
from app.domains.internship.model import Internship  # noqa: F401
from app.domains.user.model import User  # noqa: F401
from app.domains.service.model import Service  # noqa: F401
from app.domains.service_room.model import ServiceRoom  # noqa: F401
from app.domains.service_schedule.model import ServiceSchedule  # noqa: F401
from app.domains.room_schedule.model import RoomSchedule, RoomScheduleStudent  # noqa: F401
from app.domains.period.model import Period  # noqa: F401
