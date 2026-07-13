# Contributing to CyberPath AI

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your values
3. Run `make install-backend` and `make install-frontend`
4. Run `make docker-up` to start PostgreSQL
5. Run `make migrate` to apply database migrations
6. Run `make dev-backend` and `make dev-frontend`

## Branch Strategy

- `main` — production-ready code
- `develop` — integration branch
- `feature/<name>` — new features
- `bugfix/<name>` — bug fixes

## Pull Requests

Every PR should:
- Build successfully
- Pass all tests (`make test`)
- Update documentation if needed
- Follow coding standards (lint, typecheck)
- Have at least 1 approval

## Commit Convention

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `refactor:` — code refactoring
- `test:` — adding tests
- `chore:` — maintenance tasks

## Code Review

- Minimum 1 approval required
- No direct pushes to `main`
- Resolve all comments before merging

## Backend Development

- Follow PEP 8 with ruff
- Use type hints everywhere
- Write docstrings for public functions
- Keep functions small and focused
- Add tests for new features

## Frontend Development

- Use TypeScript
- Follow ESLint rules
- Write component tests with Vitest
- Keep components reusable and stateless

## Knowledge Base

- Edit JSON files in `knowledge/versions/v1/current/`
- Run `python scripts/validate_knowledge.py` after changes
- Follow schemas in `knowledge/schemas/`
