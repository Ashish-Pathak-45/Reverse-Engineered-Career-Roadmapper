from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="user", cascade="all, delete-orphan")
    project_evidence = relationship("ProjectEvidence", back_populates="user", cascade="all, delete-orphan")
    saved_profiles = relationship("SavedProfile", back_populates="user", cascade="all, delete-orphan")
    saved_resources = relationship("SavedResource", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal Information
    username = Column(String(100), unique=True, index=True, nullable=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(150), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)

    # Education
    college = Column(String(200), nullable=True)
    degree = Column(String(150), default="B.Tech Computer Science")
    specialization = Column(String(150), nullable=True)
    academic_year = Column(String(50), default="3rd Year")
    graduation_year = Column(Integer, default=2026)
    education_level = Column(String(100), default="Undergraduate")

    # Career Information
    target_career = Column(String(150), default="Machine Learning Engineer")
    career_goal = Column(String(150), default="Machine Learning Engineer")
    target_job_role = Column(String(150), default="Machine Learning Engineer")
    target_company = Column(String(150), nullable=True)
    experience_level = Column(String(100), default="Entry-Level / Student")
    internship_experience = Column(Text, nullable=True)
    technical_skills = Column(JSON, default=list)  # list of strings (self-reported)
    skills_to_develop = Column(JSON, default=list)  # list of strings
    existing_projects = Column(JSON, default=list)  # list of objects

    # Learning Preferences
    available_study_hours = Column(Integer, default=14)
    preferred_learning_style = Column(String(100), default="Hands-on Project Based")
    career_target_timeline = Column(String(100), default="12 Months")
    learning_budget = Column(String(100), default="Free & Open Source")

    # Privacy & Settings
    profile_visibility = Column(String(50), default="public")  # 'public' or 'private'
    notification_preferences = Column(JSON, default=lambda: {
        "email_milestones": True,
        "weekly_digest": True,
        "ai_recommendations": True
    })
    is_onboarded = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")  # milestone, reminder, system, feedback
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="notifications")
