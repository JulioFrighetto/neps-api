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

def seed_admin():
    password = hash_password('admin')

    sql = f"""
        INSERT OR IGNORE INTO users (name, email, password, is_active, created_at, updated_at)
        VALUES (
            "admin",
            "admin@email.com",
            "{password}",
            1,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
    """

    with engine.begin() as conn:
        conn.execute(text(sql))
