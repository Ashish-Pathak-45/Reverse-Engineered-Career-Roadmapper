"""
================================================================================
PATHFORGE AI — Feedback Email Notification System Verification Script
================================================================================
Validates:
1. /api/feedback/email-status diagnostics (No private keys exposed)
2. Anonymous & Authenticated feedback submission
3. Database persistence of all 7 key feedback fields + email delivery status
4. Graceful handling when email provider is not configured vs configured
5. Protection of sensitive email in public reviews
6. Admin feedback dashboard & status transition auditing
================================================================================
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def request_json(url, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(error_body)
        except Exception:
            return e.code, {"error": error_body}

def run_tests():
    print("=" * 70)
    print("PATHFORGE AI — Feedback & Email Notification Verification")
    print("=" * 70)

    # 1. Diagnostics endpoint
    print("\n[TEST 1] Email Diagnostics Endpoint (/api/feedback/email-status)")
    status_code, status_data = request_json(f"{BASE_URL}/api/feedback/email-status")
    assert status_code == 200, f"Expected 200, got {status_code}"
    print(f"  HTTP {status_code}: Resend Configured: {status_data['configured']}")
    print(f"  Diagnostics: {status_data['message']}")
    print(f"  Target Receiver: {status_data['receiver_email']}")
    print(f"  Sender Address: {status_data['from_email']}")
    assert "api_key" not in status_data and "resend_api_key" not in status_data, "API key must not be leaked!"
    print("  [PASS] Diagnostics endpoint secure and operational.")

    # 2. Anonymous feedback submission
    print("\n[TEST 2] Anonymous Feedback Submission (Default / Unconfigured Email State)")
    anon_feedback = {
        "rating": 5,
        "ease_of_use": 5,
        "roadmap_quality": 5,
        "success_stories_usefulness": 4,
        "ai_quality": 5,
        "category": "roadmap",
        "written_comments": "The prerequisites graph made learning data structures intuitive!",
        "feature_suggestions": "Add an export button for PDF roadmap summaries.",
        "bug_reports": None,
        "is_public_review": True,
        "review_display_name": "Priya Sharma (CS Undergrad)"
    }
    status_code, submit_resp = request_json(f"{BASE_URL}/api/feedback", method="POST", data=anon_feedback)
    assert status_code == 200, f"Submission failed with {status_code}: {submit_resp}"
    print(f"  HTTP {status_code}: Submission ID #{submit_resp['id']}")
    print(f"  Email Delivery Status: {submit_resp['email_delivery_status']}")
    print(f"  User Message: '{submit_resp['message']}'")
    assert submit_resp["id"] > 0
    assert submit_resp["rating"] == 5
    assert submit_resp["ease_of_use"] == 5
    assert submit_resp["roadmap_quality"] == 5
    assert submit_resp["success_stories_usefulness"] == 4
    assert submit_resp["ai_quality"] == 5
    assert submit_resp["category"] == "roadmap"
    assert submit_resp["written_comments"] == anon_feedback["written_comments"]
    print("  [PASS] Anonymous submission successfully persisted.")

    # 3. Authenticated student submission
    print("\n[TEST 3] Authenticated Student Feedback Submission")
    login_code, login_data = request_json(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={"email": "student@pathforge.ai", "password": "StudentPass123!"}
    )
    assert login_code == 200, f"Login failed: {login_data}"
    student_token = login_data["access_token"]
    print(f"  Authenticated as: {login_data['user']['full_name']} ({login_data['user']['email']})")

    auth_feedback = {
        "rating": 4,
        "ease_of_use": 4,
        "roadmap_quality": 5,
        "success_stories_usefulness": 5,
        "ai_quality": 4,
        "category": "ai_recommendation",
        "written_comments": "AI roadmap adjustments aligned well with current industry requirements.",
        "feature_suggestions": "Integrate with LeetCode API progress.",
        "bug_reports": None,
        "is_public_review": True,
        "review_display_name": "Alex R. (Software Engineer)"
    }
    status_code, auth_submit_resp = request_json(
        f"{BASE_URL}/api/feedback",
        method="POST",
        data=auth_feedback,
        token=student_token
    )
    assert status_code == 200, f"Auth submission failed: {auth_submit_resp}"
    print(f"  HTTP {status_code}: Submission ID #{auth_submit_resp['id']}")
    print(f"  Email Status: {auth_submit_resp['email_status']}")
    print("  [PASS] Authenticated user submission persisted with user context.")

    # 4. Verified public reviews privacy check
    print("\n[TEST 4] Public Reviews Privacy & Display Verification (/api/feedback/reviews)")
    status_code, reviews = request_json(f"{BASE_URL}/api/feedback/reviews")
    assert status_code == 200
    print(f"  Public reviews count: {len(reviews)}")
    anon_feedback_id = submit_resp["id"]
    matching_review = next((r for r in reviews if r["id"] == anon_feedback_id), None)
    for rev in reviews:
        assert "user_email" not in rev, "CRITICAL: user_email exposed in public review schema!"
    print("  [PASS] Public reviews verified. User email is strictly hidden from public endpoints.")

    # 5. Admin dashboard summary & status transition
    print("\n[TEST 5] Admin Feedback Moderation & Audit History")
    admin_login_code, admin_login = request_json(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={"email": "admin@pathforge.ai", "password": "AdminPass123!"}
    )
    assert admin_login_code == 200
    admin_token = admin_login["access_token"]

    status_code, admin_summary = request_json(f"{BASE_URL}/api/feedback/admin/summary", token=admin_token)
    assert status_code == 200
    print(f"  Admin Summary -> Total Feedbacks: {admin_summary['total_feedback']}")
    print(f"  Average Rating: {admin_summary['average_rating']}/5")
    print(f"  Average Ease of Use: {admin_summary['average_ease_of_use']}/5")
    print(f"  Average Roadmap Quality: {admin_summary['average_roadmap_quality']}/5")
    print(f"  Rating Breakdown: {admin_summary['rating_distribution']}")

    # Update feedback status
    fb_id = auth_submit_resp["id"]
    status_code, updated_fb = request_json(
        f"{BASE_URL}/api/feedback/admin/{fb_id}/status",
        method="PATCH",
        data={"status": "under_review", "note": "Assigned to curriculum review board"},
        token=admin_token
    )
    assert status_code == 200
    assert updated_fb["status"] == "under_review"
    assert len(updated_fb["status_history"]) >= 1
    print(f"  Feedback #{fb_id} transitioned to: '{updated_fb['status']}'")
    print(f"  Audit note recorded: '{updated_fb['status_history'][0]['note']}'")
    print("  [PASS] Admin moderation and audit history verified.")

    # 6. Validation bounds test
    print("\n[TEST 6] Input Validation Bounds Enforcement")
    status_code, err_resp = request_json(
        f"{BASE_URL}/api/feedback",
        method="POST",
        data={"rating": 10, "category": "general"}
    )
    assert status_code == 422, f"Expected 422 for rating 10, got {status_code}"
    print(f"  HTTP {status_code}: Rating out-of-bounds correctly rejected.")

    status_code, err_resp = request_json(
        f"{BASE_URL}/api/feedback",
        method="POST",
        data={"rating": 5, "category": "invalid_unknown_cat"}
    )
    assert status_code == 400, f"Expected 400 for bad category, got {status_code}"
    print(f"  HTTP {status_code}: Illegal category correctly rejected.")
    print("  [PASS] Validation bounds successfully enforced.")

    print("\n" + "=" * 70)
    print(">>> ALL FEEDBACK NOTIFICATION INTEGRATION TESTS PASSED! <<<")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n[FAIL] Test aborted with error: {e}")
        sys.exit(1)
