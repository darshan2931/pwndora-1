import urllib.request, urllib.parse, json, sys, uuid, ssl

API = "http://localhost:8000/api/v1"

def api_call(method, path, data=None, token=None, content_type="application/json"):
    url = f"{API}{path}"
    h = {}
    if token:
        h["Authorization"] = f"Bearer {token}"
    body = None
    if data is not None:
        if content_type == "application/json":
            body = json.dumps(data).encode()
            h["Content-Type"] = "application/json"
        else:
            body = data
            h["Content-Type"] = content_type
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(r)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        try:
            return e.code, json.loads(b)
        except:
            return e.code, b

def check(name, status, resp, expect=200):
    ok = status == expect
    sym = "OK" if ok else "FAIL"
    print(f"[{sym}] {name} -> {status}")
    if not ok or (isinstance(resp, dict) and not resp.get("success", True)):
        print(f"       {json.dumps(resp, indent=2)[:500]}")
    return ok

# 1. Register
print("=== REGISTER ===")
s, r = api_call("POST", "/auth/register", {"name": "UITest2", "email": "uitest2@test.com", "password": "Test1234!"})
check("Register", s, r)

# 2. Login
print("\n=== LOGIN ===")
login_body = urllib.parse.urlencode({"username": "uitest2@test.com", "password": "Test1234!"}).encode()
s, r = api_call("POST", "/auth/login", login_body, content_type="application/x-www-form-urlencoded")
token = r.get("access_token") if isinstance(r, dict) else None
check("Login", s, r)
if not token:
    print("FATAL: No token")
    sys.exit(1)

# 3. Auth/me
s, r = api_call("GET", "/auth/me", token=token)
check("Auth/me", s, r)

# 4. Analyze (manual skills)
print("\n=== ANALYZE CAREER ===")
boundary = uuid.uuid4().hex
body = (
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"career_goal\"\r\n\r\nPenetration Tester\r\n"
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"study_hours\"\r\n\r\n10\r\n"
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"manual_skills\"\r\n\r\nPython,Nmap,Wireshark,Linux,Bash\r\n"
    f"--{boundary}--\r\n"
).encode()
s, r = api_call("POST", "/career/analyze", body, token=token, content_type=f"multipart/form-data; boundary={boundary}")
check("Analyze Career", s, r)
analyze_data = r.get("data", {}) if isinstance(r, dict) else {}
matched = analyze_data.get("matched_skills", ["Python", "Nmap", "Wireshark", "Linux", "Bash"])
missing = analyze_data.get("missing_skills", ["Burp Suite", "Metasploit"])
readiness = analyze_data.get("career_readiness", 30)
roadmap = analyze_data.get("roadmap", [{"title": "Learn Python", "estimatedHours": 20}])
est_weeks = analyze_data.get("estimated_weeks", 12)

# 5. Save Assessment
print("\n=== SAVE ASSESSMENT ===")
save_data = {
    "career_goal": "Penetration Tester",
    "matched_skills": matched,
    "missing_skills": missing,
    "readiness_score": readiness,
    "roadmap": roadmap,
    "estimated_weeks": est_weeks,
    "study_hours": 10,
    "learning_preferences": ["labs", "video"],
}
s, r = api_call("POST", "/career/save", save_data, token=token)
check("Save Assessment", s, r)

# 6. Dashboard
print("\n=== DASHBOARD ===")
s, r = api_call("GET", "/career/dashboard", token=token)
ok = s == 200 and isinstance(r, dict) and r.get("success")
print(f"[{'OK' if ok else 'FAIL'}] Dashboard -> {s}")
if ok and r.get("data"):
    data = r["data"]
    p = data.get("profile", {})
    print(f"  name={p.get('name')}, role={p.get('targetRole')}, readiness={p.get('readiness')}")
    print(f"  known={len(p.get('knownSkills',[]))}, missing={len(p.get('missingSkills',[]))}")
    print(f"  roadmap={len(data.get('roadmap',[]))} steps, id={data.get('roadmapId')}")
elif ok:
    print("  Data is NULL!")

# 7. Mentor
print("\n=== MENTOR ===")
s, r = api_call("GET", "/mentor/greeting", token=token)
check("Mentor Greeting", s, r)

# 8. Certification Planner
print("\n=== CERT PLANNER ===")
s, r = api_call("POST", "/certifications/plan", {"weekly_hours": 10}, token=token)
ok = s == 200 and isinstance(r, dict) and r.get("success") and r.get("data", {}).get("summary", {}).get("total_certifications", 0) > 0
print(f"[{'OK' if ok else 'FAIL'}] Certification Planner -> {s}")
if isinstance(r, dict) and r.get("data"):
    plan = r["data"]
    print(f"  career={plan.get('career')}, certs={plan['summary'].get('total_certifications')}, weeks={plan['summary'].get('total_weeks')}, cost=${plan['summary'].get('total_cost')}")
    for c in plan.get("certifications", [])[:5]:
        print(f"    #{c['position']} {c['name']} ({c['difficulty']}) {c['weeks']}w ${c['cost']['total']}")
elif not ok:
    print(f"       {json.dumps(r, indent=2)[:500]}")

# 9. Log Study Hours + Weekly Progress (V2-B)
print("\n=== PROGRESS TRACKING ===")
s, r = api_call("POST", "/progress/log-study", {"hours": 3, "notes": "Protocols + NMAP lab"}, token=token)
ok = s == 200 and isinstance(r, dict) and r.get("success")
print(f"[{'OK' if ok else 'FAIL'}] Log Study Hours -> {s}")
if not ok:
    print(f"       {json.dumps(r, indent=2)[:500]}")

s, r = api_call("GET", "/progress/weekly", token=token)
ok = s == 200 and isinstance(r, dict) and r.get("success") and r.get("data", {}).get("total_hours", 0) >= 3
print(f"[{'OK' if ok else 'FAIL'}] Weekly Progress -> {s}")
if isinstance(r, dict) and r.get("data"):
    w = r["data"]
    print(f"  week={w.get('week_start')} goal={w.get('goal_hours')}h total={w.get('total_hours')}h pct={w.get('progress_pct')}%")
if not ok:
    print(f"       {json.dumps(r, indent=2)[:500]}")

s, r = api_call("POST", "/progress/goal", {"goal_hours": 15}, token=token)
ok = s == 200 and isinstance(r, dict) and r.get("success")
print(f"[{'OK' if ok else 'FAIL'}] Set Weekly Goal -> {s}")
if not ok:
    print(f"       {json.dumps(r, indent=2)[:500]}")

# 10. Portfolio
print("\n=== PORTFOLIO ===")
s, r = api_call("GET", "/progress/portfolio", token=token)
ok = s == 200 and isinstance(r, dict) and r.get("success")
print(f"[{'OK' if ok else 'FAIL'}] Portfolio -> {s}")
if isinstance(r, dict) and r.get("data"):
    print(f"  projects={len(r['data'].get('projects', []))}")
if not ok:
    print(f"       {json.dumps(r, indent=2)[:500]}")

# 11. Dashboard weekly progress should now be real
print("\n=== DASHBOARD WEEKLY (VERIFY) ===")
s, r = api_call("GET", "/career/dashboard", token=token)
ok = s == 200 and isinstance(r, dict) and r.get("success")
print(f"[{'OK' if ok else 'FAIL'}] Dashboard (verify) -> {s}")
if ok and r.get("data"):
    wp = r["data"].get("weeklyProgress", [])
    total = sum(d.get("hours", 0) for d in wp)
    print(f"  weeklyProgress={wp}")
    print(f"  total logged across week = {total}h")
if not ok:
    print(f"       {json.dumps(r, indent=2)[:500]}")

print("\n=== ALL DONE ===")
