# AI Mentor Demo Script

## Setup

1. Start backend: `uvicorn app.main:app --reload`
2. Ensure MISTRAL_API_KEY is set in `.env` (or demo fallback will be used)
3. Open API docs at `http://localhost:8000/docs`

## Demo Flow (3 minutes)

### Step 1: Career Analysis (1 min)

```bash
curl -X POST http://localhost:8000/api/v1/career/analyze \
  -F "career_goal=SOC Analyst" \
  -F "study_hours=10" \
  -F "manual_skills=Linux, Python, Networking"
```

**Show**: Career readiness score, matched skills, missing skills, AI-generated explanation.

### Step 2: AI Mentor Chat (1 min)

```bash
curl -X POST http://localhost:8000/api/v1/mentor/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How should I start learning SIEM tools?"}'
```

**Show**: Contextual AI response that references the user's profile and missing skills.

### Step 3: Roadmap Explanation (1 min)

The career analysis response includes `ai_summary` — an AI-generated explanation of why the roadmap is ordered the way it is.

**Show**: The explanation references specific skills and their dependencies.

## Key Talking Points

1. **Explainable AI**: Every recommendation has a clear reason
2. **No hallucinations**: AI only references skills from the knowledge base
3. **Contextual**: AI knows the user's profile, target role, and readiness
4. **Fallback**: If API is down, demo data is served automatically

## Sample Demo Questions for Mentor

- "What certifications should I get first?"
- "How do I build a home lab for SOC analyst work?"
- "What's the difference between SIEM and EDR?"
- "How long will it take to reach job readiness?"
