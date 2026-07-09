# Roadmap Engine Specification

## Purpose

Generate a personalized cybersecurity learning roadmap.

---

# Inputs

Career Goal

Missing Skills

Weekly Study Hours

Knowledge Base

---

# Workflow

Skill Gaps

↓

Prerequisite Resolution

↓

Learning Order

↓

Project Mapping

↓

Timeline Estimation

---

# Outputs

{
    "roadmap": [],
    "projects": [],
    "estimated_weeks": 0
}

---

# Rules

Never recommend completed skills.

Respect prerequisites.

Recommend projects after every major milestone.

Estimate duration using study hours.

---

# Timeline Formula

Skill Hours

÷

Weekly Hours

=

Estimated Weeks

---

# Acceptance Criteria

No duplicate skills

Correct order

Projects mapped

Timeline generated