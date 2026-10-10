from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Overall platform rating (1-5)")
    ease_of_use: int = Field(5, ge=1, le=5, description="Platform ease of use rating (1-5)")
    roadmap_quality: int = Field(5, ge=1, le=5, description="Roadmap quality rating (1-5)")
    success_stories_usefulness: int = Field(5, ge=1, le=5, description="Success stories rating (1-5)")
    ai_quality: int = Field(5, ge=1, le=5, description="AI recommendation quality (1-5)")
    category: str = Field("general", max_length=50, description="Category of feedback")  # general, bug, feature_request, roadmap, success_story, ai_recommendation
    feature_suggestions: Optional[str] = Field(None, max_length=3000)
    bug_reports: Optional[str] = Field(None, max_length=3000)
    written_comments: Optional[str] = Field(None, max_length=5000)
    is_public_review: bool = False
    review_display_name: Optional[str] = Field("Anonymous Student", max_length=100)
    roadmap_id: Optional[int] = None

class FeedbackUpdateStatus(BaseModel):
    status: str  # new, under_review, in_progress, resolved
    note: Optional[str] = None

class FeedbackStatusHistoryOut(BaseModel):
    id: int
    old_status: str
    new_status: str
    note: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True

class FeedbackOut(BaseModel):
    id: int
    rating: int
    ease_of_use: int
    roadmap_quality: int
    success_stories_usefulness: int
    ai_quality: int
    category: str
    status: str
    feature_suggestions: Optional[str] = None
    bug_reports: Optional[str] = None
    written_comments: Optional[str] = None
    is_public_review: bool
    review_display_name: Optional[str] = None
    roadmap_id: Optional[int] = None
    email_delivery_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackSubmissionOut(FeedbackOut):
    email_sent: bool
    email_status: str  # "sent", "failed", "not_configured"
    message: str

    class Config:
        from_attributes = True

class FeedbackAdminOut(FeedbackOut):
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    email_delivery_error: Optional[str] = None
    status_history: List[FeedbackStatusHistoryOut] = []

    class Config:
        from_attributes = True

class FeedbackAdminSummaryOut(BaseModel):
    total_feedback: int
    average_rating: float
    average_ease_of_use: float
    average_roadmap_quality: float
    rating_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
