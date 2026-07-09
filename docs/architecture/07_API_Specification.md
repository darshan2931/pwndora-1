# API Specification

## Overview

All communication between the frontend and backend is performed through REST APIs.

Base URL

/api/v1

---

# POST /career/analyze

Description

Analyze the learner profile and generate recommendations.

Request

- Resume
- Career Goal
- Weekly Study Hours

Response

- Current Skills
- Missing Skills
- Career Readiness
- Learning Roadmap
- Recommended Projects
- AI Summary

---

# POST /mentor/chat

Description

Interact with the AI Mentor.

Request

- Question
- Conversation Context

Response

- AI Answer

---

# GET /careers

Returns

Supported cybersecurity career paths.

---

# GET /knowledge/skills

Returns

Supported cybersecurity skills.

---

# GET /projects

Returns

Project recommendations.

---

# Response Format

Every API returns

status

message

data

errors

---

# Error Codes

200 Success

400 Invalid Request

401 Unauthorized

404 Not Found

500 Internal Server Error