import html
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.email_service import (
    build_html_email, build_plain_text_email, send_feedback_notification_email, is_resend_configured
)

client = TestClient(app)

def test_email_status_endpoint():
    response = client.get("/api/feedback/email-status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "message" in data
    assert "receiver_email" in data
    assert "from_email" in data

def test_html_and_text_escaping():
    malicious_input = "<script>alert('pwned')</script> & <b>test</b>"
    escaped_input = html.escape(malicious_input)

    html_email = build_html_email(
        submission_id=101,
        submission_time="2026-10-10 12:00:00 UTC",
        category_label="Career Roadmap Feedback",
        rating=4,
        ease_of_use=5,
        roadmap_quality=4,
        success_stories_usefulness=5,
        ai_quality=4,
        written_comments=malicious_input,
        feature_suggestions=malicious_input,
        bug_reports=None,
        user_name="Student <Tester>",
        user_email="tester@example.com",
        roadmap_id=7
    )

    # Raw script tag must NOT be present
    assert "<script>alert('pwned')</script>" not in html_email
    # Escaped version MUST be present
    assert escaped_input in html_email
    assert "&lt;script&gt;" in html_email
    assert "&lt;Tester&gt;" in html_email
    assert "4 / 5 Stars" in html_email
    assert "#7" in html_email

    plain_text = build_plain_text_email(
        submission_id=101,
        submission_time="2026-10-10 12:00:00 UTC",
        category_label="Career Roadmap Feedback",
        rating=4,
        ease_of_use=5,
        roadmap_quality=4,
        success_stories_usefulness=5,
        ai_quality=4,
        written_comments=malicious_input,
        feature_suggestions=None,
        bug_reports=None,
        user_name="Student",
        user_email="tester@example.com",
        roadmap_id=7
    )
    assert "Overall Platform Rating: 4/5 Stars" in plain_text
    assert "Roadmap ID: #7" in plain_text
    assert malicious_input in plain_text

def test_feedback_submission_preserves_db_when_email_not_configured():
    # With default placeholders, email should be gracefully skipped with 'not_configured'
    payload = {
        "rating": 5,
        "ease_of_use": 5,
        "roadmap_quality": 5,
        "success_stories_usefulness": 5,
        "ai_quality": 5,
        "category": "roadmap",
        "written_comments": "This roadmap layout is incredible!",
        "feature_suggestions": "Add calendar sync",
        "is_public_review": True,
        "review_display_name": "Alex P."
    }

    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["rating"] == 5
    assert data["email_sent"] is False
    assert data["email_status"] == "not_configured"
    assert "saved" in data["message"].lower()

def test_feedback_submission_with_mocked_resend_success():
    payload = {
        "rating": 4,
        "ease_of_use": 4,
        "roadmap_quality": 5,
        "success_stories_usefulness": 4,
        "ai_quality": 5,
        "category": "ai_recommendation",
        "written_comments": "AI suggestions were remarkably accurate.",
        "is_public_review": False
    }

    with patch("app.services.email_service.is_resend_configured", return_value=(True, "Configured")):
        with patch("resend.Emails.send", return_value={"id": "resend_msg_test_abc123"}) as mock_send:
            response = client.post("/api/feedback", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] > 0
            assert data["rating"] == 4
            assert data["email_sent"] is True
            assert data["email_status"] == "sent"
            assert "Thank you" in data["message"]
            assert data["email_delivery_status"] == "sent"

            # Verify Resend payload
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["subject"] == "[PATHFORGE AI] New User Feedback — 4/5 Stars"
            assert call_args["to"] == [settings.FEEDBACK_RECEIVER_EMAIL.strip()]
            assert call_args["from"] == settings.FEEDBACK_FROM_EMAIL.strip()
            assert "AI suggestions were remarkably accurate." in call_args["text"]
            assert "AI suggestions were remarkably accurate." in call_args["html"]

def test_feedback_submission_with_mocked_resend_failure_preserves_db():
    payload = {
        "rating": 3,
        "ease_of_use": 3,
        "roadmap_quality": 3,
        "success_stories_usefulness": 3,
        "ai_quality": 3,
        "category": "bug",
        "written_comments": "Encountered a minor UI issue.",
        "bug_reports": "Sidebar toggle delayed on mobile"
    }

    with patch("app.services.email_service.is_resend_configured", return_value=(True, "Configured")):
        with patch("resend.Emails.send", side_effect=Exception("Resend API rejected: Sender domain unverified")):
            response = client.post("/api/feedback", json=payload)
            # Response must still be 200 because DB write succeeded!
            assert response.status_code == 200
            data = response.json()
            assert data["id"] > 0
            assert data["email_sent"] is False
            assert data["email_status"] == "failed"
            assert "email notification could not be sent" in data["message"].lower()

def test_feedback_validation_bounds():
    # Invalid rating > 5
    invalid_rating = {
        "rating": 6,
        "category": "general"
    }
    response = client.post("/api/feedback", json=invalid_rating)
    assert response.status_code == 422

    # Invalid category
    invalid_cat = {
        "rating": 5,
        "category": "invalid_category_123"
    }
    response = client.post("/api/feedback", json=invalid_cat)
    assert response.status_code == 400
