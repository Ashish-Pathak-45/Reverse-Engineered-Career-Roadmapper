from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)  # hidden from non-admins
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="SET NULL"), nullable=True, index=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    ease_of_use = Column(Integer, nullable=False, default=5)  # 1 to 5
    roadmap_quality = Column(Integer, nullable=False, default=5)
    success_stories_usefulness = Column(Integer, nullable=False, default=5)
    ai_quality = Column(Integer, nullable=False, default=5)
    category = Column(String(50), nullable=False, default="general")  # general, bug, feature_request, roadmap, success_story, ai_recommendation
    status = Column(String(50), nullable=False, default="new")  # new, under_review, in_progress, resolved
    feature_suggestions = Column(Text, nullable=True)
    bug_reports = Column(Text, nullable=True)
    written_comments = Column(Text, nullable=True)
    is_public_review = Column(Boolean, default=False)
    review_display_name = Column(String(100), default="Anonymous Student")
    email_delivery_status = Column(String(50), default="pending", nullable=True)  # sent, failed, not_configured, pending
    email_delivery_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="feedbacks")
    roadmap = relationship("Roadmap", foreign_keys=[roadmap_id])
    status_history = relationship("FeedbackStatusHistory", back_populates="feedback", cascade="all, delete-orphan", order_by="desc(FeedbackStatusHistory.changed_at)")

class FeedbackStatusHistory(Base):
    __tablename__ = "feedback_status_history"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    changed_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    note = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    feedback = relationship("Feedback", back_populates="status_history")
