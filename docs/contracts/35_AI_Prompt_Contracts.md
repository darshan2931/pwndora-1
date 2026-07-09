# AI Prompt Contracts

## Overview

Every AI interaction follows a predefined prompt contract.

The backend owns the prompt.

The frontend never communicates directly with Mistral.

---

# Resume Analyzer

Input

Resume Text

Output

{
    "skills":[],
    "projects":[],
    "certifications":[]
}

---

# Career Explainer

Input

Career Goal

Matched Skills

Missing Skills

Roadmap

Output

Markdown

Maximum

250 words

---

# Mentor

Input

Assessment

Roadmap

Question

Output

Plain English

Maximum

200 words

---

# Resume Reviewer

Input

Resume

Career Goal

Output

Suggestions

No rewritten resume.

---

# Prompt Rules

Never invent skills.

Never invent certifications.

Never modify backend calculations.

Always explain recommendations.

Return valid JSON when requested.