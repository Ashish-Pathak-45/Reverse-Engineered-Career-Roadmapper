import time
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, get_current_user, get_current_admin, get_optional_user
from app.models.user import User
from app.models.feedback import Feedback, FeedbackStatusHistory
from app.schemas.feedback import (
    FeedbackCreate, FeedbackUpdateStatus, FeedbackOut,
    FeedbackSubmissionOut, FeedbackAdminOut, FeedbackAdminSummaryOut
)
from app.services.email_service import (
    send_feedback_notification_email, is_resend_configured
)
from app.core.config import settings

router = APIRouter(prefix="/feedback", tags=["Feedback & Admin Moderation"])

VALID_CATEGORIES = {"general", "roadmap", "success_story", "ai_recommendation", "feature_request", "bug"}
_rate_limit_records: Dict[str, List[float]] = {}

def check_rate_limit(client_id: str, max_requests: int = 10, window_seconds: float = 60.0):
    """Enforce rate limits per IP/client to prevent spam abuse."""
    now = time.time()
    timestamps = _rate_limit_records.get(client_id, [])
    timestamps = [t for t in timestamps if now - t < window_seconds]
    if len(timestamps) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many feedback submissions. Please wait a moment before trying again."
        )
    timestamps.append(now)
    _rate_limit_records[client_id] = timestamps

@router.get("/email-status")
def get_email_status():
    """Returns diagnostics on Resend configuration without exposing private keys."""
    configured, msg = is_resend_configured()
    return {
        "configured": configured,
        "message": msg,
        "has_api_key": bool(settings.RESEND_API_KEY and not settings.RESEND_API_KEY.startswith("re_your_")),
        "receiver_email": settings.FEEDBACK_RECEIVER_EMAIL,
        "from_email": settings.FEEDBACK_FROM_EMAIL
    }

@router.post("", response_model=FeedbackSubmissionOut)
@router.post("/submit", response_model=FeedbackSubmissionOut)
def submit_feedback(
    data: FeedbackCreate,
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    # 1. Rate limiting by client IP or verified user
    client_key = f"user_{user.id}" if user else f"ip_{request.client.host if request.client else 'unknown'}"
    check_rate_limit(client_key)

    # 2. Category validation
    if data.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category '{data.category}'. Allowed categories: {sorted(list(VALID_CATEGORIES))}"
        )

    # 3. Derive user identity securely from verified session (never trust client-supplied ID/email)
    user_id = user.id if user else None
    user_email = user.email if user else None
    display_name = data.review_display_name or (user.full_name if user else "Anonymous Student")

    # 4. Database persistence (Save feedback FIRST)
    feedback = Feedback(
        user_id=user_id,
        user_email=user_email,
        roadmap_id=data.roadmap_id,
        rating=data.rating,
        ease_of_use=data.ease_of_use,
        roadmap_quality=data.roadmap_quality,
        success_stories_usefulness=data.success_stories_usefulness,
        ai_quality=data.ai_quality,
        category=data.category,
        status="new",
        feature_suggestions=data.feature_suggestions,
        bug_reports=data.bug_reports,
        written_comments=data.written_comments,
        is_public_review=data.is_public_review,
        review_display_name=display_name,
        email_delivery_status="pending"
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # 5. Dispatch real email notification via Resend
    email_sent, email_status, email_error = send_feedback_notification_email(
        submission_id=feedback.id,
        rating=feedback.rating,
        ease_of_use=feedback.ease_of_use,
        roadmap_quality=feedback.roadmap_quality,
        success_stories_usefulness=feedback.success_stories_usefulness,
        ai_quality=feedback.ai_quality,
        category=feedback.category,
        written_comments=feedback.written_comments,
        feature_suggestions=feedback.feature_suggestions,
        bug_reports=feedback.bug_reports,
        user_name=user.full_name or user.username if user else None,
        user_email=user.email if user else None,
        roadmap_id=feedback.roadmap_id,
        created_at=feedback.created_at
    )

    # 6. Record delivery status in database without losing the user's submission
    feedback.email_delivery_status = email_status
    feedback.email_delivery_error = email_error
    db.commit()
    db.refresh(feedback)

    # 7. Formulate truthful response message
    if email_sent:
        user_message = "Thank you! Your feedback has been submitted successfully."
    elif email_status == "not_configured":
        user_message = "Your feedback has been saved, but email notification is not configured on the server."
    else:
        user_message = "Your feedback has been saved, but email notification could not be sent."

    return FeedbackSubmissionOut(
        id=feedback.id,
        rating=feedback.rating,
        ease_of_use=feedback.ease_of_use,
        roadmap_quality=feedback.roadmap_quality,
        success_stories_usefulness=feedback.success_stories_usefulness,
        ai_quality=feedback.ai_quality,
        category=feedback.category,
        status=feedback.status,
        feature_suggestions=feedback.feature_suggestions,
        bug_reports=feedback.bug_reports,
        written_comments=feedback.written_comments,
        is_public_review=feedback.is_public_review,
        review_display_name=feedback.review_display_name,
        roadmap_id=feedback.roadmap_id,
        email_delivery_status=feedback.email_delivery_status,
        created_at=feedback.created_at,
        email_sent=email_sent,
        email_status=email_status,
        message=user_message
    )

@router.get("/reviews", response_model=List[FeedbackOut])
def get_public_reviews(db: Session = Depends(get_db)):
    """Returns only reviews where explicit consent was given to publish publicly."""
    reviews = db.query(Feedback).filter(
        Feedback.is_public_review == True
    ).order_by(Feedback.created_at.desc()).limit(20).all()
    return reviews

@router.get("/my-submissions", response_model=List[FeedbackOut])
def get_my_feedback(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Feedback).filter(Feedback.user_id == user.id).order_by(Feedback.created_at.desc()).all()

# ================= ADMIN PROTECTED ENDPOINTS =================

@router.get("/admin/summary", response_model=FeedbackAdminSummaryOut)
def get_admin_feedback_summary(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total = db.query(Feedback).count()
    if total == 0:
        return FeedbackAdminSummaryOut(
            total_feedback=0,
            average_rating=0.0,
            average_ease_of_use=0.0,
            average_roadmap_quality=0.0,
            rating_distribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
            category_distribution={},
            status_distribution={}
        )

    avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 0.0
    avg_ease = db.query(func.avg(Feedback.ease_of_use)).scalar() or 0.0
    avg_road = db.query(func.avg(Feedback.roadmap_quality)).scalar() or 0.0

    # Rating distribution
    rating_counts = db.query(Feedback.rating, func.count(Feedback.id)).group_by(Feedback.rating).all()
    r_dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for r, count in rating_counts:
        r_dist[str(r)] = count

    # Category distribution
    cat_counts = db.query(Feedback.category, func.count(Feedback.id)).group_by(Feedback.category).all()
    c_dist = {cat: count for cat, count in cat_counts}

    # Status distribution
    status_counts = db.query(Feedback.status, func.count(Feedback.id)).group_by(Feedback.status).all()
    s_dist = {stat: count for stat, count in status_counts}

    return FeedbackAdminSummaryOut(
        total_feedback=total,
        average_rating=round(float(avg_rating), 2),
        average_ease_of_use=round(float(avg_ease), 2),
        average_roadmap_quality=round(float(avg_road), 2),
        rating_distribution=r_dist,
        category_distribution=c_dist,
        status_distribution=s_dist
    )

@router.get("/admin/all", response_model=List[FeedbackAdminOut])
def get_admin_feedback_list(
    status_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Feedback)
    if status_filter:
        query = query.filter(Feedback.status == status_filter)
    if category_filter:
        query = query.filter(Feedback.category == category_filter)
    
    feedbacks = query.order_by(Feedback.created_at.desc()).all()
    return feedbacks

@router.patch("/admin/{feedback_id}/status", response_model=FeedbackAdminOut)
def update_feedback_status(
    feedback_id: int,
    data: FeedbackUpdateStatus,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    valid_statuses = ["new", "under_review", "in_progress", "resolved"]
    if data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of {valid_statuses}"
        )

    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found.")

    old_status = fb.status
    fb.status = data.status

    # Record history audit
    audit = FeedbackStatusHistory(
        feedback_id=fb.id,
        old_status=old_status,
        new_status=data.status,
        changed_by_admin_id=admin.id,
        note=data.note
    )
    db.add(audit)
    db.commit()
    db.refresh(fb)
    return fb
