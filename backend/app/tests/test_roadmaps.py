def test_generate_and_manage_roadmap(client):
    # 1. Login as student
    login_resp = client.post("/api/auth/login", json={
        "email": "student@pathforge.ai",
        "password": "StudentPass123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Generate Roadmap
    gen_resp = client.post("/api/roadmaps/generate", headers=headers, json={
        "dream_job": "Machine Learning Engineer",
        "target_company": "Google",
        "education_level": "Undergraduate",
        "current_skills": ["Python", "Numpy"],
        "timeline": "12 Months",
        "weekly_hours": 14
    })
    assert gen_resp.status_code == 200
    roadmap_data = gen_resp.json()
    assert roadmap_data["dream_job"] == "Machine Learning Engineer"
    assert len(roadmap_data["nodes"]) >= 8
    assert len(roadmap_data["edges"]) >= 7
    roadmap_id = roadmap_data["id"]

    # 3. List roadmaps
    list_resp = client.get("/api/roadmaps", headers=headers)
    assert list_resp.status_code == 200
    assert any(r["id"] == roadmap_id for r in list_resp.json())

    # 4. Attempt to complete locked node without prereqs -> Should be blocked!
    # Find a locked node
    locked_node = next((n for n in roadmap_data["nodes"] if n["status"] == "locked"), None)
    if locked_node:
        patch_resp = client.patch(
            f"/api/roadmaps/{roadmap_id}/nodes/{locked_node['node_id']}",
            headers=headers,
            json={"status": "completed"}
        )
        assert patch_resp.status_code == 400
        assert "prerequisites are satisfied" in patch_resp.json()["detail"]

    # 5. Complete available node -> Should succeed and advance progress!
    available_node = next((n for n in roadmap_data["nodes"] if n["status"] == "available"), None)
    if available_node:
        success_resp = client.patch(
            f"/api/roadmaps/{roadmap_id}/nodes/{available_node['node_id']}",
            headers=headers,
            json={"status": "completed"}
        )
        assert success_resp.status_code == 200
        assert success_resp.json()["progress_percentage"] > 0

        # 6. Test flag milestone as needs_revision -> Should succeed
        rev_resp = client.patch(
            f"/api/roadmaps/{roadmap_id}/nodes/{available_node['node_id']}",
            headers=headers,
            json={"status": "needs_revision"}
        )
        assert rev_resp.status_code == 200
        updated_node = next((n for n in rev_resp.json()["nodes"] if n["node_id"] == available_node["node_id"]), None)
        assert updated_node is not None
        assert updated_node["status"] == "needs_revision"

    # 7. Cross-User Data Isolation: Register a second user
    import uuid
    user2_email = f"user2_{uuid.uuid4().hex[:8]}@pathforge.ai"
    signup_resp = client.post("/api/auth/signup", json={
        "email": user2_email,
        "password": "UserPass123!",
        "full_name": "Second User"
    })
    assert signup_resp.status_code == 200
    token2 = signup_resp.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 2 attempts to view User 1's roadmap -> Must be 404 Not Found!
    unauthorized_get = client.get(f"/api/roadmaps/{roadmap_id}", headers=headers2)
    assert unauthorized_get.status_code == 404

    # User 2 attempts to delete User 1's roadmap -> Must be 404 Not Found!
    unauthorized_del = client.delete(f"/api/roadmaps/{roadmap_id}", headers=headers2)
    assert unauthorized_del.status_code == 404

    # 8. User 1 deletes their roadmap -> Should succeed!
    del_resp = client.delete(f"/api/roadmaps/{roadmap_id}", headers=headers)
    assert del_resp.status_code == 200
    assert "deleted successfully" in del_resp.json()["message"]

    # Subsequent GET returns 404
    get_after_del = client.get(f"/api/roadmaps/{roadmap_id}", headers=headers)
    assert get_after_del.status_code == 404
