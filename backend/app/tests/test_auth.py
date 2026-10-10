import uuid
import io

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_signup_and_login(client):
    email = f"test_{uuid.uuid4().hex[:8]}@pathforge.ai"
    password = "SecretPassword123!"
    
    # 1. Signup with username
    signup_resp = client.post("/api/auth/signup", json={
        "email": email,
        "password": password,
        "full_name": "Test User",
        "username": f"user_{uuid.uuid4().hex[:6]}"
    })
    assert signup_resp.status_code == 200
    data = signup_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == email
    assert data["user"]["profile"]["is_onboarded"] is False

    # 2. Login
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 3. Get profile
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["full_name"] == "Test User"

def test_profile_update_and_persistence(client):
    email = f"update_{uuid.uuid4().hex[:8]}@pathforge.ai"
    password = "Password123!"
    signup = client.post("/api/auth/signup", json={
        "email": email,
        "password": password,
        "full_name": "Initial Name"
    }).json()
    token = signup["access_token"]

    # Update profile
    new_username = f"dev_{uuid.uuid4().hex[:6]}"
    update_res = client.put("/api/auth/profile", json={
        "full_name": "Updated Engineer",
        "username": new_username,
        "bio": "Building scalable distributed intelligence.",
        "location": "San Francisco, CA",
        "college": "MIT",
        "degree": "M.S. Artificial Intelligence",
        "graduation_year": 2027,
        "target_career": "Lead AI Architect",
        "available_study_hours": 20,
        "technical_skills": ["Python", "PyTorch", "Kubernetes"],
        "linkedin_url": "https://linkedin.com/in/alex",
        "github_url": "https://github.com/alex"
    }, headers={"Authorization": f"Bearer {token}"})
    assert update_res.status_code == 200
    updated_prof = update_res.json()
    assert updated_prof["bio"] == "Building scalable distributed intelligence."
    assert updated_prof["college"] == "MIT"
    assert updated_prof["target_career"] == "Lead AI Architect"
    assert updated_prof["is_onboarded"] is True

    # Verify /me reflects updates
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert me["full_name"] == "Updated Engineer"
    assert me["username"] == new_username
    assert me["profile"]["location"] == "San Francisco, CA"

def test_username_uniqueness_validation(client):
    u1_name = f"uniq_{uuid.uuid4().hex[:6]}"
    u1 = client.post("/api/auth/signup", json={
        "email": f"u1_{uuid.uuid4().hex[:8]}@pathforge.ai",
        "password": "Password123!",
        "full_name": "User One",
        "username": u1_name
    })
    assert u1.status_code == 200

    # User 2 attempts same username
    u2 = client.post("/api/auth/signup", json={
        "email": f"u2_{uuid.uuid4().hex[:8]}@pathforge.ai",
        "password": "Password123!",
        "full_name": "User Two",
        "username": u1_name
    })
    assert u2.status_code == 400
    assert "already taken" in u2.json()["detail"]

def test_avatar_upload_validation_and_removal(client):
    signup = client.post("/api/auth/signup", json={
        "email": f"avatar_{uuid.uuid4().hex[:8]}@pathforge.ai",
        "password": "Password123!",
        "full_name": "Avatar User"
    }).json()
    token = signup["access_token"]

    # Reject unsupported file type (e.g. text file)
    bad_file = io.BytesIO(b"not an image")
    bad_upload = client.post(
        "/api/auth/profile/avatar",
        files={"file": ("test.txt", bad_file, "text/plain")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert bad_upload.status_code == 400
    assert "Unsupported image format" in bad_upload.json()["detail"]

    # Valid PNG image upload
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    good_file = io.BytesIO(png_bytes)
    good_upload = client.post(
        "/api/auth/profile/avatar",
        files={"file": ("avatar.png", good_file, "image/png")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert good_upload.status_code == 200
    avatar_url = good_upload.json()["avatar_url"]
    assert avatar_url.startswith("/uploads/avatars/")

    # Remove avatar
    del_res = client.delete("/api/auth/profile/avatar", headers={"Authorization": f"Bearer {token}"})
    assert del_res.status_code == 200
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert me["avatar_url"] is None

def test_data_export_and_account_deletion(client):
    email = f"del_{uuid.uuid4().hex[:8]}@pathforge.ai"
    password = "DeletePass123!"
    signup = client.post("/api/auth/signup", json={
        "email": email,
        "password": password,
        "full_name": "Temporary User"
    }).json()
    token = signup["access_token"]

    # Data export
    export_resp = client.get("/api/auth/export-data", headers={"Authorization": f"Bearer {token}"})
    assert export_resp.status_code == 200
    exp = export_resp.json()
    assert exp["user_profile"]["email"] == email

    # Account deletion with wrong password -> rejected
    del_fail = client.request("DELETE", "/api/auth/account", json={"password": "WrongPassword!"}, headers={"Authorization": f"Bearer {token}"})
    assert del_fail.status_code == 400

    # Account deletion with correct password
    del_ok = client.request("DELETE", "/api/auth/account", json={"password": password}, headers={"Authorization": f"Bearer {token}"})
    assert del_ok.status_code == 200

    # Login should now fail
    login_fail = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_fail.status_code == 401

def test_invalid_login(client):
    resp = client.post("/api/auth/login", json={
        "email": "nonexistent@pathforge.ai",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401
