# ADR-001: FastAPI over Django/Flask

## Status

Accepted

## Context

The backend needs a Python web framework that supports async operations, automatic OpenAPI documentation, and fast development cycles.

## Decision

Use FastAPI.

## Rationale

- Native async support for concurrent Mistral API calls
- Automatic OpenAPI/Swagger docs reduce frontend-backend integration friction
- Pydantic integration provides request validation out of the box
- Lighter than Django; more structured than Flask

## Consequences

- No built-in admin panel (Django advantage) — not needed for MVP
- Must manage database sessions manually via SQLAlchemy