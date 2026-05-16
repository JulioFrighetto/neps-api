from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.security import hash_password
from app.core.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite
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


def seed_admin():
    password = hash_password("secret123")

    sql = text(
        """
        INSERT INTO users (name, email, password, role, is_active, created_at, updated_at)
        VALUES (:name, :email, :password, :role, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(email) DO UPDATE SET
            name = excluded.name,
            password = excluded.password,
            role = excluded.role,
            is_active = excluded.is_active,
            updated_at = CURRENT_TIMESTAMP
        """
    )

    with engine.begin() as conn:
        _ensure_user_role_column(conn)
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
