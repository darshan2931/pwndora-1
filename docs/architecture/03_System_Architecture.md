# System Architecture

## Architecture Overview

CyberPath AI follows a modular monolithic architecture.

The system separates responsibilities into independent modules while maintaining a single deployable backend.

---

# Components

Frontend

↓

API Layer

↓

Career Orchestrator

↓

Resume Engine

Career Engine

Recommendation Engine

AI Service

↓

Knowledge Base

↓

PostgreSQL

↓

Mistral API

---

# Major Modules

## Frontend

Handles user interaction.

Responsibilities

- Resume Upload
- Dashboard
- Roadmap Visualization
- AI Mentor

---

## Backend

Coordinates all services.

Responsibilities

- API
- Authentication
- Orchestration
- Database

---

## Resume Engine

Extracts structured information from resumes.

---

## Career Engine

Matches user skills with career requirements.

---

## Recommendation Engine

Creates learning plans and project recommendations.

---

## AI Service

Uses Mistral API to provide explanations and mentoring.

---

## Knowledge Base

Stores cybersecurity roles, skills, certifications, and learning paths.

---

# Data Flow

User

↓

Frontend

↓

Backend

↓

Resume Analysis

↓

Career Analysis

↓

Roadmap Generation

↓

AI Explanation

↓

Dashboard