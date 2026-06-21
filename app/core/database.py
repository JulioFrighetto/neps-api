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
    try:
        columns = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        has_role = any(column[1] == "role" for column in columns)
        if not has_role:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
    except Exception:
        pass

def _ensure_user_profile_columns(conn) -> None:
    try:
        columns = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        column_names = {column[1] for column in columns}

        if "internship_id" not in column_names:
            conn.execute(text("ALTER TABLE users ADD COLUMN internship_id INTEGER NULL"))
        if "education_institute_id" not in column_names:
            conn.execute(text("ALTER TABLE users ADD COLUMN education_institute_id INTEGER NULL"))
    except Exception:
        pass

def _ensure_user_timestamps(conn) -> None:
    """Garante que todos os usuários tenham timestamps válidos nos campos created_at e updated_at"""
    try:
        columns = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        column_names = {column[1] for column in columns}

        if "created_at" in column_names:
            conn.execute(text("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
        if "updated_at" in column_names:
            conn.execute(text("UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))
    except Exception:
        pass

def _rebuild_users_table_without_unique_internship_id(conn) -> None:
    indexes = conn.execute(text("PRAGMA index_list(users)")).fetchall()
    unique_internships_index_exists = False

    for index in indexes:
        if not index[2]:
            continue
        index_name = index[1]
        columns = conn.execute(text(f"PRAGMA index_info('{index_name}')")).fetchall()
        column_names = [column[2] for column in columns]
        if column_names == ["internship_id"]:
            unique_internships_index_exists = True
            break

    if not unique_internships_index_exists:
        return

    conn.execute(text("PRAGMA foreign_keys=off"))
    conn.execute(text("ALTER TABLE users RENAME TO users_legacy"))
    conn.execute(
        text(
            """
            CREATE TABLE users (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password VARCHAR(255),
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                internship_id INTEGER NULL,
                education_institute_id INTEGER NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY(internship_id) REFERENCES internships(id),
                FOREIGN KEY(education_institute_id) REFERENCES education_institutes(id)
            )
            """
        )
    )
    conn.execute(
        text(
            """
            INSERT INTO users (
                id, name, email, password, role, internship_id, education_institute_id,
                is_active, created_at, updated_at
            )
            SELECT
                id, name, email, password, role, internship_id, education_institute_id,
                is_active, created_at, updated_at
            FROM users_legacy
            """
        )
    )
    conn.execute(text("DROP TABLE users_legacy"))
    conn.execute(text("PRAGMA foreign_keys=on"))

def _ensure_room_columns(conn) -> None:
    try:
        columns = conn.execute(text("PRAGMA table_info(rooms)")).fetchall()
        column_names = {column[1] for column in columns}

        if "internship_id" not in column_names:
            conn.execute(text("ALTER TABLE rooms ADD COLUMN internship_id INTEGER NULL"))
    except Exception:
        pass

def _ensure_room_timestamps(conn) -> None:
    try:
        columns = conn.execute(text("PRAGMA table_info(rooms)")).fetchall()
        column_names = {column[1] for column in columns}

        if "created_at" in column_names:
            conn.execute(text("UPDATE rooms SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
        if "updated_at" in column_names:
            conn.execute(text("UPDATE rooms SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))
    except Exception:
        pass 

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
                internship_id INTEGER NOT NULL,
                name VARCHAR(20) NOT NULL,
                room_capacity INTEGER NOT NULL,
                has_gurney BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY(internship_id) REFERENCES internships(id)
            )
            """
        )
    )
    conn.execute(
        text(
            """
            INSERT INTO rooms (id, internship_id, name, room_capacity, has_gurney, is_active, created_at, updated_at)
            SELECT id, internship_id, name, room_capacity, has_gurney, is_active, created_at, updated_at
            FROM rooms_legacy
            """
        )
    )
    conn.execute(text("DROP TABLE rooms_legacy"))
    conn.execute(text("PRAGMA foreign_keys=on"))

def _ensure_history_columns(conn) -> None:
    try:
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
    except Exception:
        pass

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        _ensure_room_columns(conn)
        _rebuild_rooms_table_without_internship_field(conn)
        _ensure_room_timestamps(conn)
        _ensure_history_columns(conn)
        _ensure_user_role_column(conn)
        _ensure_user_profile_columns(conn)
        _ensure_user_timestamps(conn)
        _rebuild_users_table_without_unique_internship_id(conn)
        
        def _ensure_internship_columns(conn) -> None:
            columns = conn.execute(text("PRAGMA table_info(internships)")).fetchall()
            column_names = {column[1] for column in columns}
            if "name" not in column_names:
                conn.execute(text("ALTER TABLE internships ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT ''"))
            if "region_id" not in column_names:
                try:
                    conn.execute(text("ALTER TABLE internships ADD COLUMN region_id INTEGER NULL"))
                except Exception as e:
                    pass 
        
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
            if "director_signed_pdf" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN director_signed_pdf BLOB NULL"))
            if "internship_start_date" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN internship_start_date DATE NULL"))
            if "internship_expected_end_date" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN internship_expected_end_date DATE NULL"))
            if "discipline_id" not in column_names:
                try:
                    conn.execute(text("ALTER TABLE students ADD COLUMN discipline_id INTEGER NULL"))
                except Exception as e:
                    pass
            if "course_id" not in column_names:
                try:
                    conn.execute(text("ALTER TABLE students ADD COLUMN course_id INTEGER NULL"))
                except Exception as e:
                    pass
            if "internship_id" not in column_names:
                try:
                    conn.execute(text("ALTER TABLE students ADD COLUMN internship_id INTEGER NULL"))
                except Exception as e:
                    pass
        
        def _rebuild_internships_table(conn) -> None:
            columns = conn.execute(text("PRAGMA table_info(internships)")).fetchall()
            column_names = {column[1] for column in columns}
            col_defaults = {c[1]: c[4] for c in columns}
            if "course_id" not in column_names and col_defaults.get("created_at") == "CURRENT_TIMESTAMP":
                return
            conn.execute(text("PRAGMA foreign_keys=off"))
            conn.execute(text("ALTER TABLE internships RENAME TO internships_legacy"))
            conn.execute(
                text(
                    """
                    CREATE TABLE internships (
                        id INTEGER NOT NULL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        region_id INTEGER NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(region_id) REFERENCES regions(id)
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    INSERT INTO internships (id, name, region_id, is_active, created_at, updated_at)
                    SELECT id, COALESCE(name, ''), region_id, is_active, created_at, updated_at
                    FROM internships_legacy
                    """
                )
            )
            conn.execute(text("DROP TABLE internships_legacy"))
            conn.execute(text("PRAGMA foreign_keys=on"))

        _rebuild_internships_table(conn)
        _ensure_internship_columns(conn)

        def _ensure_internship_timestamps(conn) -> None:
            try:
                columns = conn.execute(text("PRAGMA table_info(internships)")).fetchall()
                column_names = {column[1] for column in columns}
                if "created_at" in column_names:
                    conn.execute(text("UPDATE internships SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
                if "updated_at" in column_names:
                    conn.execute(text("UPDATE internships SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))
            except Exception:
                pass
        _ensure_internship_timestamps(conn)

        _ensure_student_columns(conn)
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

        def _ensure_discipline_columns(conn) -> None:
            columns = conn.execute(text("PRAGMA table_info(disciplines)")).fetchall()
            column_names = {column[1] for column in columns}
            if "code" not in column_names:
                conn.execute(text("ALTER TABLE disciplines ADD COLUMN code VARCHAR(20) NULL"))
            if "region_id" not in column_names:
                conn.execute(text("ALTER TABLE disciplines ADD COLUMN region_id INTEGER NULL"))

        def _ensure_internship_columns(conn) -> None:
            columns = conn.execute(text("PRAGMA table_info(internships)")).fetchall()
            column_names = {column[1] for column in columns}
            if "name" not in column_names:
                conn.execute(text("ALTER TABLE internships ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT ''"))
            if "region_id" not in column_names:
                conn.execute(text("ALTER TABLE internships ADD COLUMN region_id INTEGER NULL"))

        _ensure_discipline_columns(conn)
        _ensure_internship_columns(conn)
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
            if "director_signed_pdf" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN director_signed_pdf BLOB NULL"))
            if "internship_start_date" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN internship_start_date DATE NULL"))
            if "internship_expected_end_date" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN internship_expected_end_date DATE NULL"))
            if "discipline_id" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN discipline_id INTEGER NULL"))
            if "professor_name" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN professor_name VARCHAR(100) NULL"))
            if "preceptor_name" not in column_names:
                conn.execute(text("ALTER TABLE students ADD COLUMN preceptor_name VARCHAR(100) NULL"))

        _ensure_student_columns(conn)

        # education_institute_courses join table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS education_institute_courses (
                education_institute_id INTEGER NOT NULL REFERENCES education_institutes(id),
                course_id INTEGER NOT NULL REFERENCES courses(id),
                PRIMARY KEY (education_institute_id, course_id)
            )
        """))

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