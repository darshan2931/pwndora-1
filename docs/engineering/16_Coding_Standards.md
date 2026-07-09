# Coding Standards

## Purpose

This document defines the coding standards followed across the CyberPath AI project.

The goal is consistency, maintainability, and readability.

---

# General Principles

- Write readable code.
- Keep functions small.
- Avoid duplicate logic.
- Prefer composition over inheritance.
- Keep business logic out of API routes.

---

# Python Standards

- Follow PEP 8.
- Use type hints.
- Write docstrings for public functions.
- Use dataclasses or Pydantic models where appropriate.

Example

```python
def analyze_resume(
    resume_text: str,
    target_role: str
) -> CareerAssessment:
    ...
```

---

# FastAPI Standards

Routes should only

- validate requests
- call orchestrator
- return response

Never place business logic inside routes.

---

# React Standards

Components should be

- reusable
- stateless whenever possible
- placed inside components/

Pages should only compose components.

---

# Naming

Files

snake_case.py

React Components

PascalCase.tsx

Variables

camelCase

Classes

PascalCase

Constants

UPPER_CASE

---

# Git

Small commits.

One feature per branch.

Never commit secrets.