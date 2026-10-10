import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PATHFORGE AI — Adaptive Career Intelligence Platform"
    TAGLINE: str = "Your Dream Career. Your Roadmap. Your Future."
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pathforge-secret-key-production-change-this-in-env-98234721")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # SQLite default for instant zero-dependency local run, supports PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pathforge.db")
    
    # AI Credentials (Optional - Heuristic Algorithmic Engine acts as live fallback if empty)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Default Admin Credentials
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@pathforge.ai")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "AdminPass123!")

    # Resend Transactional Email Notification Configuration
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "re_your_actual_api_key")
    FEEDBACK_RECEIVER_EMAIL: str = os.getenv("FEEDBACK_RECEIVER_EMAIL", "your_email@example.com")
    FEEDBACK_FROM_EMAIL: str = os.getenv("FEEDBACK_FROM_EMAIL", "your_verified_sender@example.com")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()
