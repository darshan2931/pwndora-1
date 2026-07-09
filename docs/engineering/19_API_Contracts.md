# API Contracts

## Purpose

Defines the request and response format shared between frontend and backend.

Changes must remain backward compatible during development.

---

# Standard Response

```json
{
  "success": true,
  "message": "",
  "data": {}
}
```

---

# Error Response

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": []
}
```

---

# Career Analysis Response

```json
{
  "profile": {},
  "career_readiness": 72,
  "matched_skills": [],
  "missing_skills": [],
  "roadmap": [],
  "projects": [],
  "mentor_summary": ""
}
```

---

# Versioning

Current Version

v1

Future versions should never break existing clients.