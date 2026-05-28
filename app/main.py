from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.core.models import *  # noqa: F401, F403 — registers all models with Base.metadata
from app.core.settings import settings
from app.domains.course.router import router as course_router
from app.domains.education_institute.router import router as edu_institute_router
from app.domains.region.router import router as region_router
from app.domains.service.router import router as service_router
from app.domains.service_room.router import router as service_room_router
from app.domains.service_schedule.router import router as service_schedule_router
from app.domains.room.router import router as room_router
from app.domains.room_schedule.router import router as room_schedule_router
from app.domains.student.router import router as student_router
from app.domains.user.auth_router import router as auth_router
from app.domains.user.router import router as user_router
from app.domains.period.router import router as period_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)
app.include_router(edu_institute_router, prefix=API_PREFIX)
app.include_router(course_router, prefix=API_PREFIX)
app.include_router(region_router, prefix=API_PREFIX)
app.include_router(room_schedule_router, prefix=API_PREFIX)
app.include_router(room_router, prefix=API_PREFIX)
app.include_router(service_router, prefix=API_PREFIX)
app.include_router(service_room_router, prefix=API_PREFIX)
app.include_router(service_schedule_router, prefix=API_PREFIX)
app.include_router(student_router, prefix=API_PREFIX)
app.include_router(period_router, prefix=API_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
