# Backend Architecture

## Overview

The backend is built using FastAPI and follows a modular service-based architecture.

Business logic is separated into dedicated services.

---

# Folder Structure

backend/

api/

services/

database/

knowledge/

models/

schemas/

utils/

---

# Core Services

## Resume Service

Responsibilities

- Resume Parsing
- Skill Extraction
- Profile Creation

---

## Career Service

Responsibilities

- Skill Matching
- Career Analysis
- Readiness Calculation

---

## Roadmap Service

Responsibilities

- Learning Path Generation
- Skill Ordering
- Resource Mapping

---

## Recommendation Service

Responsibilities

- Project Suggestions
- Certification Suggestions

---

## AI Service

Responsibilities

- Mistral Integration
- Prompt Management
- Mentor Chat
- Career Explanations

---

## Career Orchestrator

Coordinates all backend services.

Workflow

Resume

↓

Resume Service

↓

Career Service

↓

Roadmap Service

↓

Recommendation Service

↓

AI Service

↓

Response

---

# Database

PostgreSQL

Stores

- Users
- Assessments
- Roadmaps
- Sessions

---

# Knowledge Base

JSON Files

- roles.json
- skills.json
- projects.json
- certifications.json
- learning_paths.json