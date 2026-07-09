# Component Diagram

```mermaid
graph TB
    subgraph Frontend
        UI[Next.js UI]
        DASH[Career Dashboard]
        MENTOR[AI Mentor Chat]
    end

    subgraph Backend
        API[FastAPI Gateway]
        subgraph Services
            ORCH[Career Orchestrator]
            RESUME[Resume Service]
            CAREER[Career Service]
            ROADMAP[Roadmap Service]
            RECOMMEND[Recommendation Service]
            AI[AI Service]
        end
    end

    subgraph Storage
        DB[(PostgreSQL)]
        KB[Knowledge Base JSON]
    end

    subgraph External
        MISTRAL[Mistral API]
    end

    UI --> API
    DASH --> API
    MENTOR --> API

    API --> ORCH
    ORCH --> RESUME
    ORCH --> CAREER
    ORCH --> ROADMAP
    ORCH --> RECOMMEND
    ORCH --> AI

    RESUME --> KB
    CAREER --> KB
    ROADMAP --> KB
    RECOMMEND --> KB
    AI --> MISTRAL

    ORCH --> DB
    RESUME --> DB
    CAREER --> DB