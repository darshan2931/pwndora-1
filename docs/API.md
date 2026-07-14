# CyberPath AI — API Documentation

**Base URL:** `http://localhost:8000/api/v1`

All responses follow the format:
```json
{ "success": true, "data": { ... } }
```
Errors follow:
```json
{ "success": false, "message": "...", "errors": [...] }
```

---

## Health Check

### `GET /health`
Returns server status.

**Response:**
```json
{ "status": "ok", "version": "0.1.0" }
```

---

## Careers

### `GET /api/v1/careers`
List all available career paths.

**Response:**
```json
{
  "success": true,
  "data": [
    { "id": "application-security-engineer", "title": "Application Security Engineer", "description": "..." }
  ]
}
```

---

## Knowledge Base

### `GET /api/v1/knowledge/skills`
All skills grouped by category.

**Response:**
```json
{
  "success": true,
  "data": {
    "categories": [
      { "name": "Cloud Security", "skills": ["AWS", "Azure", "GCP"] }
    ]
  }
}
```

### `GET /api/v1/projects`
All projects.

### `GET /api/v1/projects/{skill_name}`
Projects filtered by skill (e.g. `Python`, `AWS`).

### `GET /api/v1/certifications/{role_name}`
Certifications filtered by role (e.g. `Application Security Engineer`).

---

## Career Analysis

### `POST /api/v1/career/analyze`
Submit a resume or manual skills to get a full career analysis.

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `career_goal` | string | Yes | Target career title |
| `study_hours` | int | No | Weekly study hours (default: 10) |
| `manual_skills` | string | No | Comma-separated skills |
| `resume` | file | No | PDF/DOCX/TXT resume |

> Either `resume` or `manual_skills` is required.

**Response:**
```json
{
  "success": true,
  "data": {
    "assessment": { "readiness_score": 0.65, "matched_skills": [...], "missing_skills": [...] },
    "roadmap": { "steps": [...], "total_weeks": 12 },
    "recommendations": { "projects": [...], "certifications": [...] }
  }
}
```

### `POST /api/v1/career/explain`
Get an AI-generated career explanation.

**Request body (JSON):**
```json
{ "career_goal": "Application Security Engineer", "user_skills": ["Python", "AWS"] }
```

**Response:**
```json
{ "success": true, "data": { "explanation": "...", "confidence": 0.82 } }
```

---

## Mentor Chat

### `POST /api/v1/mentor/chat`
Chat with the AI mentor about a career goal.

**Request body (JSON):**
```json
{ "question": "What skills should I learn first?", "assessment_id": "..." }
```

**Response:**
```json
{ "response": "Based on your assessment..." }
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Missing required field |
| 404 | Resource not found |
| 500 | Internal server error |
| 503 | AI service unavailable (missing API key) |
