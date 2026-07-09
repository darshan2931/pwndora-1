# Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input
        RES[Resume PDF]
        MANUAL[Manual Skills]
        GOAL[Career Goal]
        TIME[Weekly Hours]
    end

    subgraph Processing
        EXTRACT[Skill Extraction]
        MATCH[Skill Matching]
        ORDER[Skill Ordering]
        GENERATE[Roadmap Generation]
        EXPLAIN[AI Explanation]
    end

    subgraph Storage
        KB[(Knowledge Base)]
        DB[(PostgreSQL)]
    end

    subgraph Output
        SCORE[Readiness Score]
        MISSING[Missing Skills]
        ROADMAP[Learning Roadmap]
        PROJECTS[Project Recommendations]
        EXPL[AI Explanations]
    end

    RES --> EXTRACT
    MANUAL --> EXTRACT
    EXTRACT --> MATCH
    GOAL --> MATCH
    MATCH --> ORDER
    KB --> ORDER
    KB --> MATCH
    TIME --> GENERATE
    ORDER --> GENERATE
    GENERATE --> PROJECTS
    KB --> PROJECTS
    GENERATE --> EXPLAIN
    PROJECTS --> EXPLAIN
    EXPLAIN --> MISTRAL[Mistral API]
    MISTRAL --> EXPLAIN

    EXTRACT --> DB
    MATCH --> DB
    GENERATE --> DB

    MATCH --> MISSING
    MISSING --> EXSCORE[Readiness Calculation]
    EXSCORE --> EXSCORE2[Readiness Score]

    GENERATE --> ROADMAP
    MISSING --> PROJECTS

    EXSCORE --> Output
    MISSING --> Output
    ROADMAP --> Output
    PROJECTS --> Output
    EXPLAIN --> Output