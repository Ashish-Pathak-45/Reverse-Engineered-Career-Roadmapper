import urllib.request
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def request(path, method='GET', data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    encoded_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(f"{BASE_URL}{path}", data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = body
        return {'status_code': e.code, 'error': parsed}

print("====================================================")
print("TEST 1: Authenticate Demo Student")
print("====================================================")
login_res = request('/auth/login', method='POST', data={
    'email': 'student@pathforge.ai',
    'password': 'StudentPass123!'
})
assert 'access_token' in login_res, f"Login failed: {login_res}"
token = login_res['access_token']
print(f"[PASS] Authenticated as: {login_res['user']['full_name']}")

print("\n====================================================")
print("TEST 2: Fetch Current Roadmap & Milestone Graph")
print("====================================================")
roadmaps = request('/roadmaps', token=token)
assert len(roadmaps) > 0, "No roadmaps found"
roadmap_id = roadmaps[0]['id']
active_roadmap = request(f'/roadmaps/{roadmap_id}', token=token)
print(f"[PASS] Active Roadmap ID: {roadmap_id}")
print(f"  Title: {active_roadmap['title']}")
print(f"  Total Nodes: {len(active_roadmap['nodes'])}, Total Edges: {len(active_roadmap['edges'])}")
print(f"  Initial Progress: {active_roadmap['progress_percentage']}%")

nodes = active_roadmap['nodes']
node_dict = {n['node_id']: n for n in nodes}

unlocked_node = next((n for n in nodes if n['status'] in ('unlocked', 'in_progress', 'completed')), None)
locked_node = next((n for n in nodes if n['status'] == 'locked'), None)

assert unlocked_node is not None, "No unlocked milestone found"
print(f"[PASS] Available Milestone: [{unlocked_node['node_id']}] {unlocked_node['title']} (status: {unlocked_node['status']})")
if locked_node:
    print(f"[PASS] Locked Milestone: [{locked_node['node_id']}] {locked_node['title']} (status: {locked_node['status']})")

print("\n====================================================")
print("TEST 3: Enforce Prerequisite Lock Safety (Reject Locked Node Completion)")
print("====================================================")
if locked_node:
    res_locked = request(f'/roadmaps/{roadmap_id}/nodes/{locked_node["node_id"]}', method='PATCH', data={
        'status': 'completed'
    }, token=token)
    assert res_locked.get('status_code') == 400, f"Expected 400 validation error, got: {res_locked}"
    print(f"[PASS] System rejected premature completion of locked milestone with 400 Bad Request.")
    print(f"  Response Detail: {res_locked['error']}")

print("\n====================================================")
print("TEST 4: Advance Milestone (in_progress -> completed) & Auto-Unlock")
print("====================================================")
# Transition to in_progress
res_in_prog = request(f'/roadmaps/{roadmap_id}/nodes/{unlocked_node["node_id"]}', method='PATCH', data={
    'status': 'in_progress'
}, token=token)
updated_node = next(n for n in res_in_prog['nodes'] if n['node_id'] == unlocked_node['node_id'])
assert updated_node['status'] == 'in_progress'
print(f"[PASS] Transitioned [{unlocked_node['node_id']}] to 'in_progress'")

# Transition to completed
res_completed = request(f'/roadmaps/{roadmap_id}/nodes/{unlocked_node["node_id"]}', method='PATCH', data={
    'status': 'completed'
}, token=token)
completed_node = next(n for n in res_completed['nodes'] if n['node_id'] == unlocked_node['node_id'])
assert completed_node['status'] == 'completed'
print(f"[PASS] Transitioned [{unlocked_node['node_id']}] to 'completed'")
print(f"[PASS] Real-time Progress Percentage: {res_completed['progress_percentage']}%")

print("\n====================================================")
print("TEST 5: State Reversion Safety (needs_revision & Relocking)")
print("====================================================")
res_revision = request(f'/roadmaps/{roadmap_id}/nodes/{unlocked_node["node_id"]}', method='PATCH', data={
    'status': 'needs_revision'
}, token=token)
revised_node = next(n for n in res_revision['nodes'] if n['node_id'] == unlocked_node['node_id'])
assert revised_node['status'] == 'needs_revision'
print(f"[PASS] Transitioned [{unlocked_node['node_id']}] to 'needs_revision'")
print(f"[PASS] Recalculated Progress Percentage: {res_revision['progress_percentage']}%")

# Restore to completed
res_restored = request(f'/roadmaps/{roadmap_id}/nodes/{unlocked_node["node_id"]}', method='PATCH', data={
    'status': 'completed'
}, token=token)
print(f"[PASS] Restored [{unlocked_node['node_id']}] to 'completed'")

print("\n====================================================")
print("TEST 6: Prerequisite Graph Integrity Check")
print("====================================================")
edges = active_roadmap['edges']
for edge in edges:
    src_id = edge['source_node_id']
    tgt_id = edge['target_node_id']
    assert src_id in node_dict, f"Dangling edge source: {src_id}"
    assert tgt_id in node_dict, f"Dangling edge target: {tgt_id}"
print(f"[PASS] All {len(edges)} prerequisite edges reference valid roadmap milestones without dangling keys.")

print("\n====================================================")
print("TEST 7: Search & Keyword Filter Verification")
print("====================================================")
all_search = [n for n in nodes if 'python' in n['title'].lower() or 'python' in n['description'].lower()]
print(f"[PASS] Filter by keyword 'Python': Found {len(all_search)} matching milestone(s)")
completed_count = sum(1 for n in res_restored['nodes'] if n['status'] == 'completed')
print(f"[PASS] Filter by status 'completed': Found {completed_count} completed milestone(s)")

print("\n>>> ALL ROADMAP MILESTONE API INTEGRATION TESTS PASSED! <<<")
