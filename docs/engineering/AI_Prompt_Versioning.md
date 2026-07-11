# AI Prompt Versioning Strategy

## Overview

All AI prompts are stored as markdown files in `backend/ai/prompts/`. This ensures version control, human readability, and easy iteration.

## Current Prompts (v1)

| Prompt | File | Purpose |
|--------|------|---------|
| Resume Extraction | `resume.md` | Extract cybersecurity skills from resume text |
| Roadmap Explanation | `roadmap.md` | Explain why a learning roadmap order makes sense |
| Career Explanation | `career_explainer.md` | Explain career readiness to the user |
| Career Mentor | `mentor.md` | Answer career-related questions contextually |
| Resume Reviewer | `resume_reviewer.md` | Suggest resume improvements for target role |

## Versioning Rules

1. **File-based versioning**: Each prompt is a standalone `.md` file
2. **Git history**: All changes tracked via commits
3. **No in-code prompts**: Prompts are loaded from files at runtime via `_load_prompt()`
4. **A/B testing**: To test prompt variants, create `resume_v2.md` and load conditionally

## Prompt Engineering Principles

- Always provide user context in the user message, not the system prompt
- Never ask the AI to invent skills or certifications
- Request structured JSON when machine-parseable output is needed
- Validate all AI responses before returning to frontend
- Keep prompts under 200 words to minimize token usage

## Adding a New Prompt

1. Create `backend/ai/prompts/new_prompt.md`
2. Add a builder method in `PromptBuilder` class
3. Add a service method in `AIService` class
4. Write tests for the new prompt
5. Update this document

## Rollback

If a prompt change causes issues, revert the `.md` file to the previous version via git:
```bash
git log --oneline backend/ai/prompts/
git checkout <commit-hash> -- backend/ai/prompts/resume.md
```
