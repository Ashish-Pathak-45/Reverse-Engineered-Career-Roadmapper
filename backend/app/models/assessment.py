from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    topic = Column(String(100), index=True, nullable=False)
    difficulty = Column(String(50), default="Intermediate")  # Beginner, Intermediate, Advanced
    estimated_minutes = Column(Integer, default=15)
    questions = Column(JSON, default=list)  # list of {id, question, options, correct_index, explanation, skill_tested}
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")

class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # Percentage e.g. 85.0
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    answers_json = Column(JSON, default=dict)
    weak_topics = Column(JSON, default=list)  # list of skills needing revision
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="assessment_results")
    assessment = relationship("Assessment", back_populates="results")
