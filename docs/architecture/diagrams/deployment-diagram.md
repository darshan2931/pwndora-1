# Deployment Diagram

```mermaid
graph TB
    subgraph "Client Browser"
        NEXT[Next.js Static Build]
    end

    subgraph "Vercel / VPS"
        FE[Next.js Served Pages]
    end

    subgraph "Backend Server"
        API[FastAPI - Uvicorn]
        CACHE[In-Memory Cache]
    end

    subgraph "Database Server"
        PG[(PostgreSQL)]
    end

    subgraph "File System"
        KB[JSON Knowledge Base]
    end

    subgraph "External"
        MISTRAL[Mistral API]
    end

    USER --> NEXT
    NEXT --> FE
    FE --> API
    API --> CACHE
    API --> PG
    API --> KB
    API --> MISTRAL