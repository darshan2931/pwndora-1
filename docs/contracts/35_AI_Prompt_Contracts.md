# AI Prompt Contracts

## Overview

Every AI interaction follows a predefined prompt contract.

The backend owns the prompt.

The frontend never communicates directly with Mistral.

All prompts are stored as markdown files in `backend/ai/prompts/`.

---

## Resume Analyzer

**File:** `resume.md`

**Input:** Resume Text

**Output:**
```json
{
    "skills": [],
    "projects": [],
    "certifications": []
}
```

---

## Roadmap Explainer

**File:** `roadmap.md`

**Input:** Target Role, Readiness Score, Matched Skills, Missing Skills, Roadmap Steps

**Output:** Markdown (max 250 words)

---

## Career Explainer

**File:** `career_explainer.md`

**Input:** Career Goal, Readiness Score, Matched Skills, Missing Skills

**Output:** Markdown (max 250 words)

---

## Mentor

**File:** `mentor.md`

**Input:** Assessment Context, User Question

**Output:** Plain English (max 200 words)

**Features:** Multi-turn conversation with session context

---

## Resume Reviewer

**File:** `resume_reviewer.md`

**Input:** Resume Text, Career Goal

**Output:** Suggestions (no rewritten resume)

---

## Prompt Rules

- Never invent skills.
- Never invent certifications.
- Never modify backend calculations.
- Always explain recommendations.
- Return valid JSON when requested.
- Provide user context in user message, not system prompt.

---

## Versioning

Prompts are version-controlled via git. To roll back a prompt change:

```bash
git log --oneline backend/ai/prompts/
git checkout <commit-hash> -- backend/ai/prompts/<prompt>.md
```

See `docs/engineering/AI_Prompt_Versioning.md` for full strategy.
