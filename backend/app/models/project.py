from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProjectRecommendation(Base):
    __tablename__ = "project_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    target_career = Column(String(100), index=True, nullable=False)
    difficulty = Column(String(50), default="Intermediate")
    problem_statement = Column(Text, nullable=False)
    learning_objectives = Column(JSON, default=list)
    prerequisites = Column(JSON, default=list)
    dataset_requirements = Column(Text, nullable=False)
    tech_stack = Column(JSON, default=list)
    implementation_milestones = Column(JSON, default=list)
    testing_strategy = Column(Text, nullable=False)
    evaluation_metrics = Column(Text, nullable=False)
    deployment_options = Column(Text, nullable=False)
    readme_outline = Column(Text, nullable=False)
    interview_questions = Column(JSON, default=list)
    demonstrates = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ProjectEvidence(Base):
    __tablename__ = "project_evidence"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="SET NULL"), nullable=True, index=True)
    node_id = Column(String(100), nullable=True)  # milestone node key
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    related_skill = Column(String(150), nullable=False)
    evidence_type = Column(String(50), default="github")  # github, deployed_app, report, assessment, certificate, demo
    evidence_url = Column(String(500), nullable=True)
    verification_status = Column(String(50), default="submitted")  # submitted, checked, verified, needs_improvement
    evaluation_notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="project_evidence")
