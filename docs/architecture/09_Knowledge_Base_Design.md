# Knowledge Base Design

## Overview

The Knowledge Base contains structured cybersecurity information used by the Career Intelligence Engine.

It is independent from the AI model.

This ensures explainable and deterministic recommendations.

---

# Knowledge Files

roles.json

skills.json

projects.json

certifications.json

learning_paths.json

resources.json

---

# Role Structure

Each role contains

- Description
- Required Skills
- Optional Skills
- Recommended Certifications
- Suggested Projects

---

# Skill Structure

Each skill contains

- Name
- Category
- Difficulty
- Prerequisites
- Related Tools
- Learning Resources

---

# Project Structure

Each project contains

- Title
- Difficulty
- Skills Demonstrated
- Estimated Time
- GitHub Deliverables

---

# Certification Structure

Each certification contains

- Name
- Vendor
- Difficulty
- Recommended Stage
- Related Roles

---

# Learning Path Structure

Each learning path contains

- Career Goal
- Ordered Skills
- Recommended Projects
- Certifications
- Estimated Duration

---

# Design Principles

- Human curated
- Version controlled
- Explainable
- Easy to update
- Independent from AI