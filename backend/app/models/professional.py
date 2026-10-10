from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProfessionalProfile(Base):
    __tablename__ = "professional_profiles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    profile_image = Column(String(500), nullable=True)
    current_role = Column(String(200), nullable=False)
    organization = Column(String(200), nullable=False)
    category = Column(String(100), index=True, nullable=False)  # AI & Machine Learning, Software Engineering, etc.
    verified_date = Column(String(50), nullable=False)
    summary = Column(Text, nullable=False)
    bio_citation = Column(Text, nullable=False)
    education_history = Column(JSON, default=list)  # list of {degree, institution, year, verified}
    original_sources = Column(JSON, default=list)  # list of {title, url, source_type, verified_date}
    learning_takeaways = Column(JSON, default=list)  # list of strings
    suggested_student_adaptation = Column(JSON, default=dict)  # structured suggestion
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    milestones = relationship("ProfessionalMilestone", back_populates="professional", cascade="all, delete-orphan", order_by="ProfessionalMilestone.order_index")
    skills = relationship("ProfessionalSkill", back_populates="professional", cascade="all, delete-orphan")
    saved_by = relationship("SavedProfile", back_populates="professional", cascade="all, delete-orphan")

class ProfessionalMilestone(Base):
    __tablename__ = "professional_milestones"

    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professional_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    organization = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    milestone_type = Column(String(50), default="Career")  # Education, Career, Breakthrough, Founding
    order_index = Column(Integer, default=0)

    professional = relationship("ProfessionalProfile", back_populates="milestones")

class ProfessionalSkill(Base):
    __tablename__ = "professional_skills"

    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professional_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    association_type = Column(String(50), default="documented_role")  # documented_role, public_work, inferred

    professional = relationship("ProfessionalProfile", back_populates="skills")

class SavedProfile(Base):
    __tablename__ = "saved_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    professional_id = Column(Integer, ForeignKey("professional_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="saved_profiles")
    professional = relationship("ProfessionalProfile", back_populates="saved_by")
