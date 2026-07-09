# Frontend Architecture

## Overview

The frontend is built using Next.js and provides an intuitive, responsive interface for learners.

Its responsibility is to collect user information, visualize career progress, and communicate with backend APIs.

Business logic is not implemented in the frontend.

---

# Pages

Landing Page

Career Selection

Resume Upload

Dashboard

Roadmap

Projects

AI Mentor

Settings

---

# Component Structure

Navbar

Sidebar

Career Card

Resume Upload

Skill Card

Roadmap Timeline

Project Card

Career Score

Chat Window

Footer

---

# API Communication

Frontend communicates only with FastAPI.

No direct AI calls.

No direct database access.

---

# State Management

User Profile

Career Selection

Assessment Results

Roadmap

Chat History

Loading States

---

# Dashboard Layout

Career Readiness

↓

Current Skills

↓

Missing Skills

↓

Learning Roadmap

↓

Recommended Projects

↓

AI Mentor

---

# Design Goals

- Beginner Friendly
- Mobile Responsive
- Fast Navigation
- Clean Dashboard
- Accessibility