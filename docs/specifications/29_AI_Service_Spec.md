# AI Service Specification

## Purpose

Provide personalized explanations and career guidance using the Mistral API.

---

## Responsibilities

- Resume Skill Extraction (AI-powered)
- Roadmap Explanation
- Career Explanation
- Career Mentor Chat (with conversation context)
- Resume Feedback
- Confidence Scoring
- Response Caching
- Demo Fallback (when API unavailable)

---

## Inputs

- Career Assessment
- Roadmap
- Projects
- User Question
- Resume Text

---

## Outputs

- Natural Language
- JSON (when requested)
- Confidence Score (0.0 - 1.0)

---

## Prompt Flow

Backend Context

↓

Prompt Builder (loads .md templates)

↓

Mistral API (with retry logic)

↓

Response Validation (JSON parse, hallucination check)

↓

Confidence Scoring

↓

Frontend

---

## Prompt Rules

- Never invent skills.
- Never modify backend recommendations.
- Always explain reasoning.
- Return valid JSON when requested.
- Provide user context in user message, not system prompt.

---

## Error Handling

API Timeout / Network Error

↓

Retry up to 2 times (3 total attempts)

↓

Return Demo Fallback Response

Invalid JSON Response

↓

Return Demo Fallback Response

API Key Missing

↓

Service returns 503

---

## Caching

- Response cache with 5-minute TTL
- Cache key based on prompt content hash
- Applies to: resume extraction, roadmap explanation, career explanation

---

## Conversation Context

- Multi-turn mentor chat with session management
- History stored in memory (dict by session_id)
- Maximum 20 messages per session
- Context includes user profile, readiness, and skills

---

## Acceptance Criteria

- Consistent Output
- No Hallucinated Skills
- Response < 5 seconds (cached responses instant)
- Graceful fallback when API unavailable
- Confidence score on all explanations
