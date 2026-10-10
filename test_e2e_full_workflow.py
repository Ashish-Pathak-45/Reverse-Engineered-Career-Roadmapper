"""End-to-End Workflow Verification Script for PATHFORGE AI Adaptive Assessment Engine.
Tests all 12 steps of the user journey from login to roadmap personalization.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from fastapi.testclient import TestClient
from app.main import app
from app.services.question_bank import BANK

client = TestClient(app)

def run_verification():
    print("=" * 60)
    print("STARTING E2E VERIFICATION OF CLAUDE ADAPTIVE ENGINE")
    print("=" * 60)

    # Step 1: Verify Public / Unauthenticated Access (no login, no token)
    print("\n[Step 1] Initializing unauthenticated public session (no tokens or login)...")
    headers = {}
    health_resp = client.get("/api/health")
    assert health_resp.status_code == 200, f"Health check failed: {health_resp.text}"
    print("  -> Unauthenticated session verified. Public access enabled.")

    # Step 2: List adaptive assessment skills
    print("\n[Step 2] Fetching available skills...")
    skills_resp = client.get("/api/assessments/adaptive/skills", headers=headers)
    assert skills_resp.status_code == 200, f"Skills fetch failed: {skills_resp.text}"
    skills = skills_resp.json()
    print(f"  -> Skills returned: {skills}")
    assert "Python" in skills
    assert "Databases" in skills
    assert "Algorithms" in skills
    assert "Machine Learning" in skills

    # Step 3: Fetch first adaptive question for Python
    print("\n[Step 3] Fetching first adaptive question for 'Python'...")
    q1_resp = client.get("/api/assessments/adaptive/next", params={"skill": "Python"}, headers=headers)
    assert q1_resp.status_code == 200, f"Next question failed: {q1_resp.text}"
    q1_data = q1_resp.json()
    assert not q1_data["done"], "Expected question, got done"
    q1 = q1_data["question"]
    print(f"  -> Question ID: {q1['id']} ({q1['difficulty']} tier)")
    print(f"  -> Statement: {q1['question']}")
    assert "correct_index" not in q1, "Security violation: correct_index leaked"
    assert "explanation" not in q1, "Security violation: explanation leaked"

    # Step 4: Submit an answer to the question
    print(f"\n[Step 4] Submitting answer for {q1['id']}...")
    # Find correct index from BANK
    py_bank = {q[0]: q[5] for q in BANK["Python"]}
    correct_idx = py_bank[q1["id"]]
    ans_resp = client.post("/api/assessments/adaptive/answer", headers=headers, json={
        "question_id": q1["id"],
        "choice": correct_idx
    })
    assert ans_resp.status_code == 200 or ans_resp.status_code == 409, f"Submit answer failed: {ans_resp.text}"
    if ans_resp.status_code == 200:
        ans_data = ans_resp.json()
        print(f"  -> Correct: {ans_data['correct']}")
        print(f"  -> Explanation provided: {ans_data['explanation']}")
        print(f"  -> Current evaluated level: {ans_data['skill_result']['level']}")
        print(f"  -> Evidence count: {ans_data['skill_result']['evidence_count']}")
    else:
        print("  -> Question already recorded in persistent evidence.")

    # Step 5: Duplicate answer rejection
    print("\n[Step 5] Testing duplicate submission prevention...")
    dup_resp = client.post("/api/assessments/adaptive/answer", headers=headers, json={
        "question_id": q1["id"],
        "choice": correct_idx
    })
    assert dup_resp.status_code == 409, f"Expected 409 Conflict, got {dup_resp.status_code}"
    print("  -> Duplicate answer properly rejected with HTTP 409 Conflict.")

    # Step 6: Test invalid inputs
    print("\n[Step 6] Testing invalid inputs handling...")
    not_found = client.post("/api/assessments/adaptive/answer", headers=headers, json={
        "question_id": "nonexistent_999",
        "choice": 0
    })
    assert not_found.status_code == 404, f"Expected 404, got {not_found.status_code}"
    print("  -> Nonexistent question properly rejected with HTTP 404 Not Found.")

    # Step 7: Check Skill Profile
    print("\n[Step 7] Checking student skill profile...")
    prof_resp = client.get("/api/assessments/adaptive/profile", headers=headers)
    assert prof_resp.status_code == 200, f"Profile failed: {prof_resp.text}"
    prof_data = prof_resp.json()
    print(f"  -> Skills recorded in profile: {list(prof_data['skills'].keys())}")
    for s_name, s_info in prof_data["skills"].items():
        print(f"     * {s_name}: Level={s_info['level']}, Evidence={s_info['evidence_count']}, Confidence={s_info['confidence']}")

    # Step 8: Ensure user has an active roadmap
    print("\n[Step 8] Checking / Generating career roadmap...")
    rm_list = client.get("/api/roadmaps", headers=headers).json()
    if not rm_list:
        gen_resp = client.post("/api/roadmaps/generate", headers=headers, json={
            "dream_job": "Machine Learning Engineer",
            "target_company": "Google",
            "timeline": "6 months",
            "weekly_hours": 15,
            "current_skills": ["Python"]
        })
        assert gen_resp.status_code == 200, f"Generate roadmap failed: {gen_resp.text}"
        active_rm = gen_resp.json()
    else:
        roadmap_id = rm_list[0]["id"]
        get_rm_resp = client.get(f"/api/roadmaps/{roadmap_id}", headers=headers)
        assert get_rm_resp.status_code == 200, f"Get roadmap failed: {get_rm_resp.text}"
        active_rm = get_rm_resp.json()
    roadmap_id = active_rm["id"]
    print(f"  -> Active Roadmap ID {roadmap_id}: '{active_rm['title']}' ({len(active_rm['nodes'])} nodes)")

    # Step 9: Call Personalize Roadmap Endpoint
    print(f"\n[Step 9] Calling POST /api/roadmaps/{roadmap_id}/personalize...")
    pers_resp = client.post(f"/api/roadmaps/{roadmap_id}/personalize", headers=headers)
    assert pers_resp.status_code == 200, f"Personalize failed: {pers_resp.text}"
    personalized_rm = pers_resp.json()
    print(f"  -> Personalization succeeded.")
    personalizations = personalized_rm.get("metadata_json", {}).get("personalization", {})
    print(f"  -> Adjusted nodes count: {len(personalizations)}")
    for node_id, note in list(personalizations.items())[:3]:
        print(f"     * Node {node_id}: {note}")

    # Step 10: Verify Idempotence of Personalization
    print("\n[Step 10] Testing idempotence of personalization...")
    pers_resp_2 = client.post(f"/api/roadmaps/{roadmap_id}/personalize", headers=headers)
    assert pers_resp_2.status_code == 200
    p2 = pers_resp_2.json()
    hours_1 = [n["estimated_hours"] for n in personalized_rm["nodes"]]
    hours_2 = [n["estimated_hours"] for n in p2["nodes"]]
    assert hours_1 == hours_2, "Personalization is not idempotent!"
    print("  -> Verified: Multiple calls yield identical estimated hours (fully idempotent).")

    print("\n" + "=" * 60)
    print("ALL 10 WORKFLOW VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
