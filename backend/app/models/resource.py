from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    provider = Column(String(150), nullable=False)
    topic = Column(String(100), index=True, nullable=False)
    difficulty = Column(String(50), default="All Levels")
    format = Column(String(50), default="course")  # course, book, documentation, video, interactive
    is_free = Column(Boolean, default=True)
    cost_info = Column(String(100), default="Free / Open Source")
    source_url = Column(String(500), nullable=False)
    verified_date = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    saved_by = relationship("SavedResource", back_populates="resource", cascade="all, delete-orphan")

class SavedResource(Base):
    __tablename__ = "saved_resources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="saved_resources")
    resource = relationship("Resource", back_populates="saved_by")
