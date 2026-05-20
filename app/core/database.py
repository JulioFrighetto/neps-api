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


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
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

        _ensure_education_institute_columns(conn)
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
