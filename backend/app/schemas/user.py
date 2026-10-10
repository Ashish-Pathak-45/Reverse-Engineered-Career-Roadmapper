from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileBase(BaseModel):
    # Personal Information
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Education
    education_level: Optional[str] = "Undergraduate"
    degree: Optional[str] = "B.Tech Computer Science"
    college: Optional[str] = None
    specialization: Optional[str] = None
    academic_year: Optional[str] = "3rd Year"
    graduation_year: Optional[int] = 2026

    # Career Information
    target_career: Optional[str] = "Machine Learning Engineer"
    career_goal: Optional[str] = "Machine Learning Engineer"
    target_job_role: Optional[str] = "Machine Learning Engineer"
    target_company: Optional[str] = None
    experience_level: Optional[str] = "Entry-Level / Student"
    internship_experience: Optional[str] = None
    technical_skills: Optional[List[str]] = Field(default_factory=list)
    skills_to_develop: Optional[List[str]] = Field(default_factory=list)
    existing_projects: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    # Learning Preferences
    available_study_hours: Optional[int] = 14
    preferred_learning_style: Optional[str] = "Hands-on Project Based"
    career_target_timeline: Optional[str] = "12 Months"
    learning_budget: Optional[str] = "Free & Open Source"

    # Privacy & Settings
    profile_visibility: Optional[str] = "public"
    notification_preferences: Optional[Dict[str, bool]] = Field(default_factory=lambda: {
        "email_milestones": True,
        "weekly_digest": True,
        "ai_recommendations": True
    })
    is_onboarded: Optional[bool] = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    education_level: Optional[str] = None
    degree: Optional[str] = None
    college: Optional[str] = None
    specialization: Optional[str] = None
    academic_year: Optional[str] = None
    graduation_year: Optional[int] = None

    target_career: Optional[str] = None
    career_goal: Optional[str] = None
    target_job_role: Optional[str] = None
    target_company: Optional[str] = None
    experience_level: Optional[str] = None
    internship_experience: Optional[str] = None
    technical_skills: Optional[List[str]] = None
    skills_to_develop: Optional[List[str]] = None
    existing_projects: Optional[List[Dict[str, Any]]] = None

    available_study_hours: Optional[int] = None
    preferred_learning_style: Optional[str] = None
    career_target_timeline: Optional[str] = None
    learning_budget: Optional[str] = None

    profile_visibility: Optional[str] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    is_onboarded: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if len(v) < 3 or len(v) > 30:
                raise ValueError("Username must be between 3 and 30 characters.")
            if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
                raise ValueError("Username may only contain letters, numbers, underscores, dashes, and periods.")
        return v

    @field_validator("available_study_hours")
    @classmethod
    def validate_hours(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 80):
            raise ValueError("Available study hours per week must be between 1 and 80.")
        return v

    @field_validator("graduation_year")
    @classmethod
    def validate_grad_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1970 or v > 2045):
            raise ValueError("Graduation year must be between 1970 and 2045.")
        return v

class UserProfileOut(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserOut(UserBase):
    id: int
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    profile: Optional[UserProfileOut] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class PasswordResetRequest(BaseModel):
    email: EmailStr
    new_password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class AccountDeleteRequest(BaseModel):
    password: str

class AvatarUploadResponse(BaseModel):
    avatar_url: str
    message: str
