# AI Service Specification

## Purpose

Provide personalized explanations and career guidance using the Mistral API.

---

# Responsibilities

Resume Summary

Roadmap Explanation

Career Mentor

Project Explanation

Resume Feedback

---

# Inputs

Career Assessment

Roadmap

Projects

User Question

---

# Outputs

Natural Language

JSON (when requested)

---

# Prompt Flow

Backend Context

↓

Prompt Builder

↓

Mistral API

↓

Validation

↓

Frontend

---

# Prompt Rules

Never invent skills.

Never modify backend recommendations.

Always explain reasoning.

Return JSON when requested.

---

# Error Handling

API Timeout

↓

Retry Once

↓

Return Friendly Error

Invalid JSON

↓

Attempt Repair

↓

Reject Response

---

# Acceptance Criteria

Consistent Output

No Hallucinated Skills

Response < 5 Seconds