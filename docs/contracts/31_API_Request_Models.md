# API Request Models

## Overview

This document defines every request model accepted by the backend.

All requests use JSON unless file upload is required.

---

# Career Analysis Request

POST /api/v1/career/analyze

Content-Type

multipart/form-data

Fields

career_goal

string

Required

study_hours

integer

Required

resume

file

Optional

manual_skills

string[]

Optional

Example

{
    "career_goal":"Penetration Tester",
    "study_hours":10,
    "manual_skills":[
        "Linux",
        "Python"
    ]
}

---

# Mentor Chat Request

POST

/api/v1/mentor/chat

{
    "assessment_id":"uuid",
    "question":"Why should I learn Burp Suite?"
}

---

# Resume Upload

POST

/api/v1/resume/upload

multipart/form-data

Fields

resume

career_goal

study_hours

---

# Authentication

Reserved for future implementation.