from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    dream_job = Column(String(200), nullable=False)
    target_company = Column(String(200), nullable=False)
    timeline = Column(String(100), default="12 Months")
    weekly_hours = Column(Integer, default=14)
    current_phase = Column(String(100), default="Phase 1: Foundations")
    progress_percentage = Column(Float, default=0.0)
    starting_skill_assessment = Column(Text, nullable=True)
    completion_criteria = Column(Text, nullable=True)
    suggested_next_action = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="roadmaps")
    nodes = relationship("RoadmapNode", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapNode.order_index")
    edges = relationship("RoadmapEdge", back_populates="roadmap", cascade="all, delete-orphan")
    sprints = relationship("WeeklySprint", back_populates="roadmap", cascade="all, delete-orphan", order_by="WeeklySprint.week_number")

class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(100), nullable=False, index=True)  # unique per roadmap e.g. "node_1"
    title = Column(String(200), nullable=False)
    category = Column(String(100), default="Core Skills")
    difficulty = Column(String(50), default="Intermediate")  # Beginner, Intermediate, Advanced
    estimated_hours = Column(Integer, default=20)
    status = Column(String(50), default="locked")  # locked, available, in_progress, completed, needs_revision
    description = Column(Text, nullable=False)
    deliverable = Column(Text, nullable=False)
    completion_criteria = Column(Text, nullable=False)
    recommended_next_action = Column(Text, nullable=True)
    phase = Column(String(100), default="Phase 1")
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    order_index = Column(Integer, default=0)
    is_self_reported = Column(Boolean, default=False)
    assessment_score = Column(Float, nullable=True)
    resources = Column(JSON, default=list)  # list of {title, url, type, is_free}
    practical_assignments = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    roadmap = relationship("Roadmap", back_populates="nodes")

class RoadmapEdge(Base):
    __tablename__ = "roadmap_edges"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    source_node_id = Column(String(100), nullable=False)
    target_node_id = Column(String(100), nullable=False)
    edge_type = Column(String(50), default="prerequisite")  # prerequisite, recommended

    roadmap = relationship("Roadmap", back_populates="edges")

class WeeklySprint(Base):
    __tablename__ = "weekly_sprints"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    goals = Column(JSON, default=list)
    tasks = Column(JSON, default=list)  # list of {id, text, completed, estimated_hours, node_id}
    planned_hours = Column(Integer, default=14)
    completed_hours = Column(Integer, default=0)
    status = Column(String(50), default="active")  # active, completed, reviewed
    review_notes = Column(JSON, default=dict)  # {completed_summary, difficulties, time_spent, next_adjustments}
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    roadmap = relationship("Roadmap", back_populates="sprints")
