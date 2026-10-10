def test_feedback_flow_and_admin_security(client):
    # 1. Submit public review as student
    student_login = client.post("/api/auth/login", json={
        "email": "student@pathforge.ai",
        "password": "StudentPass123!"
    })
    assert student_login.status_code == 200
    student_token = student_login.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    fb_resp = client.post("/api/feedback", headers=student_headers, json={
        "rating": 5,
        "ease_of_use": 5,
        "roadmap_quality": 5,
        "success_stories_usefulness": 5,
        "ai_quality": 5,
        "category": "roadmap",
        "feature_suggestions": "Add export to calendar",
        "written_comments": "Exceptional roadmap tool!",
        "is_public_review": True,
        "review_display_name": "Verified Student"
    })
    assert fb_resp.status_code == 200
    fb_id = fb_resp.json()["id"]

    # 2. Public reviews should include this review without leaking private user email
    public_resp = client.get("/api/feedback/reviews")
    assert public_resp.status_code == 200
    assert any(r["id"] == fb_id for r in public_resp.json())
    for r in public_resp.json():
        assert "user_email" not in r  # Email must never be in public schema!

    # 3. Student attempts to access admin dashboard -> MUST BE FORBIDDEN (403)
    admin_summary_attempt = client.get("/api/feedback/admin/summary", headers=student_headers)
    assert admin_summary_attempt.status_code == 403
    assert "Administrative privileges required" in admin_summary_attempt.json()["detail"]

    # 4. Login as Admin
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@pathforge.ai",
        "password": "AdminPass123!"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 5. Admin accesses dashboard summary -> 200 OK with distributions
    summary_resp = client.get("/api/feedback/admin/summary", headers=admin_headers)
    assert summary_resp.status_code == 200
    summary_data = summary_resp.json()
    assert summary_data["total_feedback"] >= 1
    assert "rating_distribution" in summary_data

    # 6. Admin updates feedback status to in_progress
    patch_status = client.patch(
        f"/api/feedback/admin/{fb_id}/status",
        headers=admin_headers,
        json={"status": "in_progress", "note": "Assigned to roadmap design sprint"}
    )
    assert patch_status.status_code == 200
    assert patch_status.json()["status"] == "in_progress"
    assert len(patch_status.json()["status_history"]) >= 1
