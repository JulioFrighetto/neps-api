from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.security import hash_password
from app.core.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_user_role_column(conn) -> None:
    columns = conn.execute(text("PRAGMA table_info(users)")).fetchall()
    has_role = any(column[1] == "role" for column in columns)
    if not has_role:
        conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))


def _ensure_user_profile_columns(conn) -> None:
    columns = conn.execute(text("PRAGMA table_info(users)")).fetchall()
    column_names = {column[1] for column in columns}

    if "service_id" not in column_names:
        conn.execute(text("ALTER TABLE users ADD COLUMN service_id INTEGER NULL"))
    if "education_institute_id" not in column_names:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN education_institute_id INTEGER NULL")
        )


def _ensure_room_columns(conn) -> None:
    columns = conn.execute(text("PRAGMA table_info(rooms)")).fetchall()
    column_names = {column[1] for column in columns}

    if "service_id" not in column_names:
        conn.execute(text("ALTER TABLE rooms ADD COLUMN service_id INTEGER NULL"))


def _ensure_room_timestamps(conn) -> None:
    columns = conn.execute(text("PRAGMA table_info(rooms)")).fetchall()
    column_names = {column[1] for column in columns}

    if "created_at" in column_names:
        conn.execute(text("UPDATE rooms SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
    if "updated_at" in column_names:
        conn.execute(text("UPDATE rooms SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))


def _rebuild_rooms_table_without_internship_field(conn) -> None:
    columns = conn.execute(text("PRAGMA table_info(rooms)")).fetchall()
    column_names = [column[1] for column in columns]

    if "internship_field_id" not in column_names:
        return

    conn.execute(text("PRAGMA foreign_keys=off"))
    conn.execute(text("ALTER TABLE rooms RENAME TO rooms_legacy"))
    conn.execute(
        text(
            """
            CREATE TABLE rooms (
                id INTEGER NOT NULL PRIMARY KEY,
                service_id INTEGER NOT NULL,
                name VARCHAR(20) NOT NULL,
                room_capacity INTEGER NOT NULL,
                has_gurney BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY(service_id) REFERENCES services(id)
            )
            """
        )
    )
    conn.execute(
        text(
            """
            INSERT INTO rooms (id, service_id, name, room_capacity, has_gurney, is_active, created_at, updated_at)
            SELECT id, service_id, name, room_capacity, has_gurney, is_active, created_at, updated_at
            FROM rooms_legacy
            """
        )
    )
    conn.execute(text("DROP TABLE rooms_legacy"))
    conn.execute(text("PRAGMA foreign_keys=on"))


def _ensure_history_columns(conn) -> None:
    columns = conn.execute(text("PRAGMA table_info(histories)")).fetchall()
    column_names = {column[1] for column in columns}

    if not column_names:
        return

    if "schedule_id" not in column_names:
        conn.execute(text("ALTER TABLE histories ADD COLUMN schedule_id INTEGER NULL"))

    if "room_id" not in column_names:
        conn.execute(text("ALTER TABLE histories ADD COLUMN room_id INTEGER NULL"))

    conn.execute(
        text(
            """
            UPDATE histories
            SET schedule_id = (
                SELECT schedules.id
                FROM schedules
                WHERE schedules.room_id = histories.room_id
                LIMIT 1
            )
            WHERE schedule_id IS NULL AND room_id IS NOT NULL
            """
        )
    )

    if "created_at" in column_names:
        conn.execute(text("UPDATE histories SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
    if "updated_at" in column_names:
        conn.execute(text("UPDATE histories SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        _ensure_room_columns(conn)
        _rebuild_rooms_table_without_internship_field(conn)
        _ensure_room_timestamps(conn)
        _ensure_history_columns(conn)
    seed_admin()


def seed_admin():
    password = hash_password("secret123")

    sql = text(
        """
        INSERT INTO users (name, email, password, role, is_active, created_at, updated_at)
        VALUES (:name, :email, :password, :role, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(email) DO NOTHING
        """
    )

    with engine.begin() as conn:
        _ensure_user_role_column(conn)
        _ensure_user_profile_columns(conn)
        # Ensure education_institutes contact columns exist when model was extended
        def _ensure_education_institute_columns(conn) -> None:
            columns = conn.execute(text("PRAGMA table_info(education_institutes)")).fetchall()
            column_names = {column[1] for column in columns}
            if "cnpj" not in column_names:
                conn.execute(text("ALTER TABLE education_institutes ADD COLUMN cnpj VARCHAR(30) NULL"))
            if "address" not in column_names:
                conn.execute(text("ALTER TABLE education_institutes ADD COLUMN address VARCHAR(255) NULL"))
            if "phone" not in column_names:
                conn.execute(text("ALTER TABLE education_institutes ADD COLUMN phone VARCHAR(50) NULL"))
            if "email" not in column_names:
                conn.execute(text("ALTER TABLE education_institutes ADD COLUMN email VARCHAR(150) NULL"))
            if "priority" not in column_names:
                conn.execute(text("ALTER TABLE education_institutes ADD COLUMN priority INTEGER NOT NULL DEFAULT 0"))
            if "is_active" not in column_names:
                conn.execute(text("ALTER TABLE education_institutes ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"))

        def _ensure_course_columns(conn) -> None:
            columns = conn.execute(text("PRAGMA table_info(courses)")).fetchall()
            column_names = {column[1] for column in columns}
            if "code" not in column_names:
                conn.execute(text("ALTER TABLE courses ADD COLUMN code VARCHAR(20) NULL"))
            if "region_id" not in column_names:
                conn.execute(text("ALTER TABLE courses ADD COLUMN region_id INTEGER NULL"))

        _ensure_course_columns(conn)

        _ensure_education_institute_columns(conn)

        def _ensure_student_columns(conn) -> None:
            columns = conn.execute(text("PRAGMA table_info(students)")).fetchall()
            column_names = {column[1] for column in columns}
            if "name" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN name VARCHAR(100) NULL"))
            if "cpf" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN cpf VARCHAR(20) NULL"))
            if "email" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN email VARCHAR(150) NULL"))
            if "phone" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN phone VARCHAR(20) NULL"))
            if "semester" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN semester INTEGER NULL"))
            if "document_url" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN document_url VARCHAR(500) NOT NULL DEFAULT ''"))

        _ensure_student_columns(conn)
        conn.execute(
            sql,
            {
                "name": "Admin",
                "email": "alexdonay@gmail.com",
                "password": password,
                "role": "admin",
                "is_active": 1,
            },
        )
