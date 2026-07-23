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

print("\n=== ALL DONE ===")
