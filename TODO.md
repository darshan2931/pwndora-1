# TODO

> Tasks organized by development phase and team role.

---

## Phase 1 — Foundation

*Repository, Documentation, Knowledge Base*

### Shrovan (Backend Architect)

- [x] Set up repository structure & branch protection rules
- [x] Configure CI/CD pipelines (GitHub Actions): lint, typecheck, test
- [x] Finalize backend directory layout and module conventions
- [x] Create `.env.example` with all required variables
- [x] Set up Docker Compose with hot-reload volumes
- [x] Write `Dockerfile` for backend (Python 3.12 slim)
- [x] Write `Dockerfile` for frontend (Node multi-stage)

### Jaishree (Backend Developer)

- [ ] Design and write knowledge base YAML schemas:
  - [ ] `knowledge/roles/` — cybersecurity role definitions
  - [ ] `knowledge/skills/` — skill taxonomy with prerequisites & categories
  - [ ] `knowledge/projects/` — project catalog with difficulty & skill mapping
  - [ ] `knowledge/certifications/` — certification mappings to roles & skills
  - [ ] `knowledge/resources/` — curated learning resources per skill
- [ ] Implement `backend/knowledge/` loader to read and validate YAML files
- [ ] Write knowledge validation script (`scripts/validate_knowledge.py`)

### Darshan (AI Engineer)

- [ ] Refine Mistral prompt templates in `backend/ai/prompts/`
- [ ] Implement proper `ResponseValidator.validate_no_hallucinations()` logic
- [ ] Write prompt evaluation tests (edge cases, malformed responses)

### Aathira (Frontend Engineer)

- [x] Scaffold Next.js `app/` directory with layout and global styles
- [x] Set up Tailwind theme (colors, fonts, spacing) aligned with brand
- [x] Create shared UI primitives: Button, Input, Card, Badge, Modal
- [x] Set up path aliases (`@/components`, `@/lib`, etc.)
- [x] Configure Vitest with test utilities and helpers
- [x] Write landing page (`/`) with hero, features, and CTA

---

## Phase 2 — Backend Core

*Career Engine, Resume Parser, API Layer*

### Shrovan (Backend Architect)

- [x] Create `app/main.py` — FastAPI app factory with CORS, middleware, exception handlers
- [x] Implement Pydantic schemas in `schemas/`:
  - [x] `CareerAnalysisRequest` / `CareerAnalysisResponse`
  - [x] `ResumeUploadResponse`
  - [x] `RoadmapResponse`
  - [x] `MentorRequest` / `MentorResponse`
  - [x] `HealthResponse`
- [x] Wire up router registration in `app/main.py`
- [x] Set up Alembic and generate initial migration
- [x] Add `chat_history` and `knowledge_cache` tables to SQLAlchemy models

### Jaishree (Backend Developer)

- [ ] Implement `ResumeService`:
  - [ ] PDF parsing with `pdfminer.six`
  - [ ] DOCX parsing with `python-docx`
  - [ ] Skill extraction via keyword matching against knowledge base
  - [ ] Project/certification/experience detection
- [ ] Implement `CareerService`:
  - [ ] Skill matching between user profile and target role
  - [ ] Readiness score calculation
  - [ ] Gap analysis & learning priority ranking
- [ ] Implement `RoadmapService`:
  - [ ] Skill dependency resolution (prerequisite ordering)
  - [ ] Weekly study plan generation
  - [ ] Estimated completion timeline
  - [ ] Project mapping per skill
- [ ] Implement `RecommendationService`:
  - [ ] Project recommendations based on skill gaps
  - [ ] Certification recommendations based on target career

### Darshan (AI Engineer)

- [ ] Integrate AI enrichment into skill extraction (LLM-based extraction fallback)
- [ ] Build AI-powered career explanation endpoint
- [ ] Build AI mentor chat endpoint with conversation context

### Aathira (Frontend Engineer)

- [x] Build Resume Upload page (`/upload`)
  - [x] File drag-and-drop zone
  - [x] Upload progress indicator
  - [x] Manual skill entry fallback
- [x] Build Career Assessment page (`/assess`)
  - [x] Career selector dropdown
  - [x] Weekly hours input
  - [x] Results summary card

---

## Phase 3 — API & Integration

*Route Handlers, Frontend-Backend Wiring, Roadmap UI*

### Shrovan (Backend Architect)

- [x] Implement all API route handlers in `api/`:
  - [x] `GET /health` — health check
  - [x] `POST /api/v1/career/analyze` — full career analysis
  - [x] `GET /api/v1/careers` — list all careers
  - [x] `GET /api/v1/projects?skill=` — filter projects
  - [x] `POST /api/v1/mentor/chat` — AI mentor conversation
  - [x] `POST /api/v1/resume/upload` — resume parsing
  - [x] `GET /api/v1/roadmap/{id}` — retrieve stored roadmap
- [x] Add request rate limiting & input validation
- [x] Add structured logging middleware

### Jaishree (Backend Developer)

- [ ] Write backend unit tests:
  - [ ] Domain model tests
  - [ ] Service layer tests (mocked repos)
  - [ ] Knowledge loader tests
  - [ ] Resume parser tests (sample PDF/DOCX fixtures)
- [ ] Write backend integration tests:
  - [ ] API endpoint tests (using `TestClient`)
  - [ ] Database CRUD tests

### Darshan (AI Engineer)

- [ ] Write AI service unit tests:
  - [ ] Prompt builder output verification
  - [ ] Response validation edge cases
  - [ ] Mocked Mistral API tests
- [ ] Add confidence scoring to AI explanations

### Aathira (Frontend Engineer)

- [x] Build Dashboard page (`/dashboard`)
  - [x] Readiness score gauge
  - [x] Skill match / gap breakdown chart
  - [x] Quick action cards
- [x] Build Roadmap page (`/roadmap`)
  - [x] Timeline view of weekly steps
  - [x] Skill dependency graph
  - [x] Project cards linked to each step
  - [x] Progress tracking (planned vs completed)
- [x] Build Mentor Chat page (`/mentor`)
  - [x] Chat message list
  - [x] Input bar with send
  - [x] Suggested questions carousel
- [x] Build Career Explorer page (`/explore`)
  - [x] Career cards with readiness indicators
  - [x] Skill comparison view
- [x] Connect all frontend pages to backend API
- [x] Write frontend component tests:
  - [x] CareerCard, SkillCard, ProjectCard
  - [x] RoadmapTimeline
  - [x] ChatWindow
  - [x] ResumeUpload

---

## Phase 4 — Polish & Deploy

*Testing, Optimization, Deployment*

### Shrovan (Backend Architect)

- [x] Set up Vercel deployment for frontend
- [x] Set up Docker-based deployment for backend
- [x] Configure managed PostgreSQL (Supabase / Neon / RDS)
- [x] Add health check endpoints for container orchestration
- [x] Configure secrets in deployment environment

### Jaishree (Backend Developer)

- [ ] Performance optimize knowledge base queries (caching layer)
- [ ] Add request/response logging
- [ ] Error handling refinement (structured error responses)
- [ ] Finalize Alembic migrations for production schema

### Darshan (AI Engineer)

- [ ] Tune Mistral prompts based on test results
- [ ] Add fallback models (if Mistral API is down)
- [ ] Implement response caching for common AI queries
- [ ] Document AI prompt versioning strategy

### Aathira (Frontend Engineer)

- [x] Responsive design pass (mobile, tablet, desktop)
- [x] Loading states & skeleton screens
- [x] Error boundaries & fallback UI
- [x] Accessibility audit (keyboard nav, aria labels, contrast)
- [x] Performance audit (bundle size, image optimization, lazy loading)

---

## Phase 5 — Launch

*Hackathon Demo, Presentation, Public Release*

### Shrovan

- [x] Final security review (env vars, API keys, input sanitization)
- [x] Update LICENSE, SECURITY.md, CONTRIBUTING.md
- [x] Tag release `v1.0.0`

### Jaishree

- [ ] Verify seed data covers all 6 supported careers
- [ ] Run full test suite & fix any failures
- [ ] Generate API documentation via FastAPI auto-docs

### Darshan

- [ ] Demo script for AI mentor flow
- [ ] Prepare explainable AI examples for presentation
- [ ] Final prompt version freeze

### Aathira

- [x] Final UI polish pass
- [x] Demo walkthrough video / screenshots
- [x] Deploy frontend to Vercel production

---

## Future Versions

### V2 — Post-MVP

- [ ] **GitHub Analysis** — connect GitHub, analyze project repos
- [ ] **Certification Planner** — timeline & cost estimator for certs
- [ ] **Progress Tracking** — save & resume roadmap progress

### V3 — Advanced

- [ ] **Job Intelligence** — real-time job market skill demand
- [ ] **Interview Simulator** — AI-powered mock interviews
- [ ] **Learning Analytics** — study patterns & optimization

### V4 — Enterprise

- [ ] **University Dashboard** — batch student tracking for educators
- [ ] **Enterprise Portal** — team upskilling management
- [ ] **Recruiter Dashboard** — candidate skill verification
