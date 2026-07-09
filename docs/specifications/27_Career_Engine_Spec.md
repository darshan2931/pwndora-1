# Career Engine Specification

## Purpose

Determine how closely a user's profile matches a selected cybersecurity role.

---

# Inputs

User Skills

Career Goal

Knowledge Base

---

# Workflow

Current Skills

↓

Role Requirements

↓

Skill Matching

↓

Gap Analysis

↓

Career Readiness Score

---

# Outputs

{
    "matched_skills": [],
    "missing_skills": [],
    "recommended_order": [],
    "career_readiness": 0
}

---

# Readiness Formula

Readiness

=

Matched Skills

÷

Required Skills

×

100

---

# Responsibilities

Compare Skills

Detect Gaps

Rank Missing Skills

Calculate Readiness

---

# Error Cases

Unknown Career

↓

Return 404

No Skills

↓

Return Empty Assessment

---

# Acceptance Criteria

Correct Readiness

Correct Missing Skills

Correct Skill Matching