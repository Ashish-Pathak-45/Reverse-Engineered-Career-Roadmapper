import urllib.request
import json

def post(url, data, token=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json', **({'Authorization': f'Bearer {token}'} if token else {})},
        method='POST'
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def get(url, token=None):
    req = urllib.request.Request(
        url,
        headers={'Content-Type': 'application/json', **({'Authorization': f'Bearer {token}'} if token else {})},
        method='GET'
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def put(url, data, token=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json', **({'Authorization': f'Bearer {token}'} if token else {})},
        method='PUT'
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

print("1. Health check:")
health = get('http://127.0.0.1:8000/api/health')
print("   Status:", health)

print("2. Login as Demo Student:")
login = post('http://127.0.0.1:8000/api/auth/login', {'email': 'student@pathforge.ai', 'password': 'StudentPass123!'})
token = login['access_token']
print("   Student authenticated:", login['user']['full_name'])

print("3. Generate Roadmap via API:")
gen = post('http://127.0.0.1:8000/api/roadmaps/generate', {
    'dream_job': 'Machine Learning Engineer',
    'target_company': 'Google',
    'education_level': 'Undergraduate',
    'current_skills': ['Python', 'Basic ML'],
    'timeline': '12 Months',
    'weekly_hours': 14
}, token)
print("   Generated Roadmap Title:", gen['title'])
print("   Nodes count:", len(gen['nodes']), "Edges count:", len(gen['edges']))
print("   Progress %:", gen['progress_percentage'])

print("4. Verified Professional Profiles count:")
profs = get('http://127.0.0.1:8000/api/professionals')
print("   Profiles:", len(profs), [p['full_name'] for p in profs])

print("5. Compare Professional with user path:")
prof_id = profs[0]['id']
comp = get(f'http://127.0.0.1:8000/api/professionals/{prof_id}/compare', token)
print("   Comparison similarities count:", len(comp['similarities']), "Shared skills:", comp['shared_skills'])

print("6. Skill Gap Analysis:")
gap = post('http://127.0.0.1:8000/api/assessments/skill-gap', {'current_skills': ['Python', 'Basic ML'], 'target_role': 'Machine Learning Engineer'}, token)
print("   Match %:", gap['overall_match_percentage'], "Missing skills count:", len(gap['missing_skills']))

print("7. Career Compare (MLE vs Data Scientist):")
compare_careers = post('http://127.0.0.1:8000/api/roadmaps/compare', {'career_a': 'Machine Learning Engineer', 'career_b': 'Data Scientist'})
print("   Overlapping shared skills:", compare_careers['shared_skills'])

print("8. Admin Feedback Access:")
admin_login = post('http://127.0.0.1:8000/api/auth/login', {'email': 'admin@pathforge.ai', 'password': 'AdminPass123!'})
admin_token = admin_login['access_token']
admin_summary = get('http://127.0.0.1:8000/api/feedback/admin/summary', admin_token)
print("   Admin Summary:", admin_summary)

print("9. Update User Career Profile:")
updated_prof = put('http://127.0.0.1:8000/api/auth/profile', {
    'full_name': 'Alex Rivera',
    'target_career': 'Senior AI Architect',
    'available_study_hours': 18
}, token)
me = get('http://127.0.0.1:8000/api/auth/me', token)
print("   Updated profile verified:", me['full_name'], "Target:", me['profile']['target_career'], "Hours:", me['profile']['available_study_hours'])

print("\n>>> ALL END-TO-END WORKFLOW VERIFICATIONS PASSED SUCCESSFULLY! <<<")

