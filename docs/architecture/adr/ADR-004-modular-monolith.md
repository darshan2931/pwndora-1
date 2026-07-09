# ADR-004: Modular Monolith over Microservices

## Context

The system has four internal services (Resume, Career, Roadmap, Recommendation) plus an AI Service. They could be deployed independently or as a single unit.

## Decision

Deploy as a modular monolith — separate Python modules/services within a single FastAPI process.

## Rationale

- No network overhead between services (function calls vs HTTP)
- Simpler development, debugging, and deployment for a 4-person team
- Single deployment artifact — no Docker Compose complexity for MVP
- Services are still separated by module, so extraction to microservices is possible later

## Consequences

- Scaling means scaling the entire monolith (acceptable for MVP traffic)
- One buggy service can crash the whole process — mitigated by service-level error boundaries
- If traffic demands independent scaling later, services can be split along module boundaries