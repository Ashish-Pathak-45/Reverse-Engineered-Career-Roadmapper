import os
import html
import logging
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timezone
from app.core.config import settings

logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "general": "General Feedback",
    "roadmap": "Career Roadmap Feedback",
    "success_story": "Success Story Feedback",
    "ai_recommendation": "AI Recommendation Feedback",
    "feature_request": "Feature Request",
    "bug": "Bug Report",
}

def escape_val(val: Optional[Any], default: str = "Not provided") -> str:
    """Escapes user provided values for safe HTML rendering."""
    if val is None:
        return default
    s = str(val).strip()
    if not s:
        return default
    return html.escape(s)

def build_plain_text_email(
    submission_id: int,
    submission_time: str,
    category_label: str,
    rating: int,
    ease_of_use: int,
    roadmap_quality: int,
    success_stories_usefulness: int,
    ai_quality: int,
    written_comments: Optional[str],
    feature_suggestions: Optional[str],
    bug_reports: Optional[str],
    user_name: Optional[str],
    user_email: Optional[str],
    roadmap_id: Optional[int]
) -> str:
    """Constructs the plain-text alternative of the feedback notification email."""
    user_str = user_name.strip() if user_name and user_name.strip() else "Not provided"
    email_str = user_email.strip() if user_email and user_email.strip() else "Not provided"
    roadmap_str = f"#{roadmap_id}" if roadmap_id is not None else "Not provided"

    return f"""PATHFORGE AI — NEW FEEDBACK SUBMISSION
==================================================

Submission ID: #{submission_id}
Submission Date and Time: {submission_time}
Feedback Category: {category_label}
Overall Platform Rating: {rating}/5 Stars
Ease of Use: {ease_of_use}/5
Generated Roadmap Quality: {roadmap_quality}/5
Success Stories Usefulness: {success_stories_usefulness}/5
AI Recommendation Quality: {ai_quality}/5

Authenticated User: {user_str}
User Email: {email_str}
Roadmap ID: {roadmap_str}

Written Comments:
{written_comments.strip() if written_comments and written_comments.strip() else "Not provided"}

Feature Suggestions:
{feature_suggestions.strip() if feature_suggestions and feature_suggestions.strip() else "Not provided"}

Bug Reports:
{bug_reports.strip() if bug_reports and bug_reports.strip() else "Not provided"}

==================================================
PATHFORGE AI — Adaptive Career Intelligence Platform
"Your Dream Career. Your Roadmap. Your Future."
"""

def build_html_email(
    submission_id: int,
    submission_time: str,
    category_label: str,
    rating: int,
    ease_of_use: int,
    roadmap_quality: int,
    success_stories_usefulness: int,
    ai_quality: int,
    written_comments: Optional[str],
    feature_suggestions: Optional[str],
    bug_reports: Optional[str],
    user_name: Optional[str],
    user_email: Optional[str],
    roadmap_id: Optional[int]
) -> str:
    """Constructs a professional, responsive HTML email template with escaped user input."""
    # Star visualization
    gold_stars = "★" * rating + "☆" * (5 - rating)
    
    # Safe HTML-escaped values
    comments_escaped = escape_val(written_comments)
    suggestions_escaped = escape_val(feature_suggestions)
    bug_reports_escaped = escape_val(bug_reports)
    user_name_escaped = escape_val(user_name)
    user_email_escaped = escape_val(user_email)
    roadmap_str = f"#{roadmap_id}" if roadmap_id is not None else "Not provided"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PATHFORGE AI — New Feedback Submission</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f8fafc; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
          
          <!-- Header -->
          <tr>
            <td style="background-color: #0f172a; padding: 28px 32px; text-align: left; border-bottom: 3px solid #6366f1;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td>
                    <div style="font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #818cf8; text-transform: uppercase; margin-bottom: 4px;">
                      PATHFORGE AI &bull; PLATFORM INTELLIGENCE
                    </div>
                    <div style="font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                      New User Feedback Submission
                    </div>
                    <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
                      Your Dream Career. Your Roadmap. Your Future.
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Summary Hero Banner -->
          <tr>
            <td style="padding: 24px 32px; background-color: #f1f5f9; border-bottom: 1px solid #e2e8f0;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td>
                    <span style="display: inline-block; padding: 4px 10px; background-color: #e0e7ff; color: #4338ca; font-size: 12px; font-weight: 700; border-radius: 6px; text-transform: uppercase;">
                      {html.escape(category_label)}
                    </span>
                    <div style="margin-top: 10px; font-size: 24px; font-weight: 800; color: #0f172a;">
                      <span style="color: #f59e0b;">{gold_stars}</span>
                      <span style="font-size: 18px; margin-left: 8px; color: #334155;">{rating} / 5 Stars</span>
                    </div>
                  </td>
                  <td align="right" style="vertical-align: top;">
                    <span style="font-size: 12px; color: #64748b;">Submission ID</span>
                    <div style="font-size: 16px; font-weight: 700; color: #0f172a;">#{submission_id}</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Detailed Ratings Matrix -->
          <tr>
            <td style="padding: 28px 32px 12px 32px;">
              <div style="font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px;">
                Ratings & Experience Breakdown
              </div>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; font-size: 14px;">
                <tr style="border-bottom: 1px solid #f1f5f9;">
                  <td style="padding: 10px 0; color: #475569; font-weight: 600;">Overall Platform Rating</td>
                  <td align="right" style="padding: 10px 0; font-weight: 700; color: #0f172a;">{rating} / 5</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                  <td style="padding: 10px 0; color: #475569;">Ease of Use</td>
                  <td align="right" style="padding: 10px 0; font-weight: 700; color: #0f172a;">{ease_of_use} / 5</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                  <td style="padding: 10px 0; color: #475569;">Quality of Generated Roadmaps</td>
                  <td align="right" style="padding: 10px 0; font-weight: 700; color: #0f172a;">{roadmap_quality} / 5</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                  <td style="padding: 10px 0; color: #475569;">Usefulness of Success Stories</td>
                  <td align="right" style="padding: 10px 0; font-weight: 700; color: #0f172a;">{success_stories_usefulness} / 5</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; color: #475569;">AI Recommendation Quality</td>
                  <td align="right" style="padding: 10px 0; font-weight: 700; color: #0f172a;">{ai_quality} / 5</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Written Comments -->
          <tr>
            <td style="padding: 16px 32px;">
              <div style="font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                Written Comments / Experience
              </div>
              <div style="background-color: #f8fafc; border-left: 4px solid #6366f1; border-radius: 4px; padding: 14px 18px; font-size: 14px; line-height: 1.6; color: #1e293b; font-style: italic;">
                {comments_escaped}
              </div>
            </td>
          </tr>

          <!-- Suggestions & Bug Reports (if provided) -->
          <tr>
            <td style="padding: 12px 32px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="padding-bottom: 12px;">
                    <span style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;">Feature Suggestions:</span>
                    <div style="margin-top: 4px; font-size: 13px; color: #334155; line-height: 1.5;">{suggestions_escaped}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding-bottom: 12px;">
                    <span style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;">Reported Bug / Issue:</span>
                    <div style="margin-top: 4px; font-size: 13px; color: #334155; line-height: 1.5;">{bug_reports_escaped}</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- User & Context Metadata -->
          <tr>
            <td style="padding: 16px 32px 28px 32px;">
              <div style="background-color: #f1f5f9; border-radius: 8px; padding: 16px 20px;">
                <div style="font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
                  Submission Metadata
                </div>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="font-size: 13px; line-height: 1.6;">
                  <tr>
                    <td style="color: #64748b; width: 140px;">Authenticated User:</td>
                    <td style="color: #0f172a; font-weight: 600;">{user_name_escaped}</td>
                  </tr>
                  <tr>
                    <td style="color: #64748b;">User Email:</td>
                    <td style="color: #0f172a; font-weight: 600;">{user_email_escaped}</td>
                  </tr>
                  <tr>
                    <td style="color: #64748b;">Roadmap ID:</td>
                    <td style="color: #0f172a; font-weight: 600;">{roadmap_str}</td>
                  </tr>
                  <tr>
                    <td style="color: #64748b;">Submitted At:</td>
                    <td style="color: #0f172a;">{submission_time}</td>
                  </tr>
                </table>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 32px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #94a3b8;">
              This notification was generated automatically by PATHFORGE AI upon user feedback submission.<br>
              Direct questions or admin actions can be performed in the PATHFORGE AI Admin Console.
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

def is_resend_configured() -> Tuple[bool, str]:
    """
    Checks if Resend configuration is present and valid (not using default placeholders).
    Returns (is_ready, reason_message).
    """
    api_key = (settings.RESEND_API_KEY or "").strip()
    receiver = (settings.FEEDBACK_RECEIVER_EMAIL or "").strip()
    sender = (settings.FEEDBACK_FROM_EMAIL or "").strip()

    if not api_key or api_key == "re_your_actual_api_key" or api_key.startswith("re_your_"):
        return False, "RESEND_API_KEY is missing or set to placeholder ('re_your_actual_api_key')."
    
    if not receiver or receiver == "your_email@example.com" or "@" not in receiver:
        return False, "FEEDBACK_RECEIVER_EMAIL is missing or set to placeholder ('your_email@example.com')."

    if not sender or sender == "your_verified_sender@example.com" or "@" not in sender:
        return False, "FEEDBACK_FROM_EMAIL is missing or set to placeholder ('your_verified_sender@example.com')."

    return True, "Resend is configured."

def send_feedback_notification_email(
    submission_id: int,
    rating: int,
    ease_of_use: int,
    roadmap_quality: int,
    success_stories_usefulness: int,
    ai_quality: int,
    category: str,
    written_comments: Optional[str] = None,
    feature_suggestions: Optional[str] = None,
    bug_reports: Optional[str] = None,
    user_name: Optional[str] = None,
    user_email: Optional[str] = None,
    roadmap_id: Optional[int] = None,
    created_at: Optional[datetime] = None
) -> Tuple[bool, str, Optional[str]]:
    """
    Dispatches a real email notification via Resend for a submitted feedback form.
    Returns:
        (email_sent: bool, email_status: str, error_details: Optional[str])
        where email_status is 'sent', 'failed', or 'not_configured'.
    """
    ready, reason = is_resend_configured()
    if not ready:
        logger.info(f"Resend notification skipped: {reason}")
        return False, "not_configured", reason

    # Prepare readable values
    category_label = CATEGORY_LABELS.get(category, category.replace("_", " ").title())
    time_str = created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if created_at else datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Subject line as requested: [PATHFORGE AI] New User Feedback — 5/5 Stars
    subject = f"[PATHFORGE AI] New User Feedback — {rating}/5 Stars"

    # Build plain text and HTML templates
    plain_text = build_plain_text_email(
        submission_id=submission_id,
        submission_time=time_str,
        category_label=category_label,
        rating=rating,
        ease_of_use=ease_of_use,
        roadmap_quality=roadmap_quality,
        success_stories_usefulness=success_stories_usefulness,
        ai_quality=ai_quality,
        written_comments=written_comments,
        feature_suggestions=feature_suggestions,
        bug_reports=bug_reports,
        user_name=user_name,
        user_email=user_email,
        roadmap_id=roadmap_id
    )

    html_content = build_html_email(
        submission_id=submission_id,
        submission_time=time_str,
        category_label=category_label,
        rating=rating,
        ease_of_use=ease_of_use,
        roadmap_quality=roadmap_quality,
        success_stories_usefulness=success_stories_usefulness,
        ai_quality=ai_quality,
        written_comments=written_comments,
        feature_suggestions=feature_suggestions,
        bug_reports=bug_reports,
        user_name=user_name,
        user_email=user_email,
        roadmap_id=roadmap_id
    )

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY.strip()

        params: Dict[str, Any] = {
            "from": settings.FEEDBACK_FROM_EMAIL.strip(),
            "to": [settings.FEEDBACK_RECEIVER_EMAIL.strip()],
            "subject": subject,
            "text": plain_text,
            "html": html_content,
        }

        logger.info(
            f"Attempting Resend delivery for Feedback #{submission_id} "
            f"from '{settings.FEEDBACK_FROM_EMAIL}' to '{settings.FEEDBACK_RECEIVER_EMAIL}'"
        )
        
        response = resend.Emails.send(params)

        email_id = None
        if isinstance(response, dict):
            email_id = response.get("id")
        elif hasattr(response, "id"):
            email_id = getattr(response, "id")

        logger.info(f"Feedback email notification sent successfully via Resend. Resend Email ID: {email_id}")
        return True, "sent", None

    except Exception as e:
        err_msg = str(e)
        # Sanitize error to prevent accidental key leakage
        if settings.RESEND_API_KEY and settings.RESEND_API_KEY in err_msg:
            err_msg = err_msg.replace(settings.RESEND_API_KEY, "[REDACTED_API_KEY]")
        
        logger.error(f"Failed to deliver feedback email via Resend: {err_msg}")
        return False, "failed", err_msg
