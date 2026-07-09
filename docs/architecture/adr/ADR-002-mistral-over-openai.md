# ADR-002: Mistral over OpenAI

## Context

The AI layer requires a cost-effective, privacy-conscious LLM provider for generating career explanations and mentor responses.

## Decision

Use Mistral API.

## Rationale

- Lower cost per token compared to OpenAI
- Competitive quality for structured explanation tasks
- No data retention on user content
- Simplified prompt control without system prompt instruction-following issues
- Sufficient for the explanation-only scope (AI does not make decisions)

## Consequences

- No support for multimodal inputs (not needed)
- Must handle API rate limits and potential outages via fallback logic