# Security Policy

## Reporting Vulnerabilities

Report security issues privately via email to the project maintainers.
Do not open public GitHub issues for security vulnerabilities.

---

## Secrets Management

Never commit the following to version control:

- API Keys (MISTRAL_API_KEY, MISTRAL_API_KEYS)
- Database credentials (DATABASE_URL)
- Secret keys (SECRET_KEY)
- JWT tokens

Use environment variables or a secrets manager in production.

---

## Input Validation

All user inputs are validated via Pydantic schemas.
Resume uploads are limited to 5MB and validated by file type.

---

## Rate Limiting

API endpoints are rate-limited to 60 requests per minute per IP.
Burst protection limits to 10 requests per second.

---

## Dependencies

Update dependencies regularly via Dependabot.
Use only trusted, well-maintained packages.

---

## Authentication

JWT-based authentication is reserved for future versions.
Current MVP relies on rate limiting and input validation.

---

## Data Privacy

- Resume files are processed in memory and deleted immediately after parsing
- No user data is stored without explicit consent
- AI interactions are not logged with personal data
