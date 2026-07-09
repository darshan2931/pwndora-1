# Database Design

## Overview

PostgreSQL stores user-specific information.

Cybersecurity knowledge is stored separately in JSON files.

---

# Tables

## Users

- id
- name
- email
- created_at

---

## Assessments

- id
- user_id
- career_goal
- readiness_score
- created_at

---

## Roadmaps

- id
- assessment_id
- roadmap_json

---

## Chat History

- id
- assessment_id
- question
- response
- timestamp

---

# Relationships

User

↓

Assessment

↓

Roadmap

↓

Chat History

---

# Design Principles

- Normalize user data
- Store generated roadmaps
- Keep AI conversations separate
- Never duplicate knowledge base data