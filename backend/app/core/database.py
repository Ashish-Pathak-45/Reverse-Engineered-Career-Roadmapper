from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_auto_migrations():
    """
    Safely adds missing columns to existing SQLite database tables
    without dropping existing user data.
    """
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    with engine.connect() as conn:
        # Check users table
        try:
            res = conn.execute(text("PRAGMA table_info(users)"))
            user_cols = {row[1] for row in res.fetchall()}
            if "username" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(100)"))
            if "avatar_url" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url TEXT"))
            conn.commit()
        except Exception:
            pass

        # Check user_profiles table
        try:
            res = conn.execute(text("PRAGMA table_info(user_profiles)"))
            profile_cols = {row[1] for row in res.fetchall()}
            
            new_profile_cols = [
                ("username", "VARCHAR(100)"),
                ("avatar_url", "TEXT"),
                ("bio", "TEXT"),
                ("location", "VARCHAR(150)"),
                ("linkedin_url", "VARCHAR(255)"),
                ("github_url", "VARCHAR(255)"),
                ("portfolio_url", "VARCHAR(255)"),
                ("specialization", "VARCHAR(150)"),
                ("academic_year", "VARCHAR(50)"),
                ("career_goal", "VARCHAR(150)"),
                ("target_job_role", "VARCHAR(150)"),
                ("target_company", "VARCHAR(150)"),
                ("experience_level", "VARCHAR(100)"),
                ("skills_to_develop", "JSON"),
                ("profile_visibility", "VARCHAR(50) DEFAULT 'public'"),
                ("notification_preferences", "JSON"),
                ("is_onboarded", "BOOLEAN DEFAULT 1"),
            ]

            for col_name, col_type in new_profile_cols:
                if col_name not in profile_cols:
                    conn.execute(text(f"ALTER TABLE user_profiles ADD COLUMN {col_name} {col_type}"))
            conn.commit()
        except Exception:
            pass

        # Check feedbacks table
        try:
            res = conn.execute(text("PRAGMA table_info(feedbacks)"))
            fb_cols = {row[1] for row in res.fetchall()}
            if "roadmap_id" not in fb_cols:
                conn.execute(text("ALTER TABLE feedbacks ADD COLUMN roadmap_id INTEGER"))
            if "email_delivery_status" not in fb_cols:
                conn.execute(text("ALTER TABLE feedbacks ADD COLUMN email_delivery_status VARCHAR(50) DEFAULT 'pending'"))
            if "email_delivery_error" not in fb_cols:
                conn.execute(text("ALTER TABLE feedbacks ADD COLUMN email_delivery_error TEXT"))
            conn.commit()
        except Exception:
            pass
