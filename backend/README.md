# CyberPath AI Backend

## Structure

```
app/
  main.py               # FastAPI entry point
  domain/               # Shared domain models (single source of truth)
    models.py
api/                     # Route definitions
ai/                      # AI service (Darshan's module)
  client.py
  prompt_builder.py
  response_validator.py
  prompts/               # Prompt templates (.md)
config/                  # Environment configs
core/                    # Core settings
database/                # DB session, migrations
models/                  # SQLAlchemy ORM models
orchestrators/           # Cross-service coordination (CareerOrchestrator)
repositories/            # Database access layer
schemas/                 # Pydantic request/response schemas
services/                # Business logic (Resume, Career, Roadmap, Recommendation)
utils/                   # Shared utilities
tests/                   # Test suite
```

## Domain Models

`app/domain/models.py` defines shared dataclasses used by every layer:
- Skill, Career, UserProfile, Assessment, Roadmap, Project

## Local Development

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```