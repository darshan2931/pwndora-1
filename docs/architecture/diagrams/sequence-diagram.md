# Sequence Diagram — Full Career Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as FastAPI
    participant ORCH as Orchestrator
    participant RESUME as Resume Service
    participant CAREER as Career Service
    participant ROADMAP as Roadmap Service
    participant REC as Recommendation Service
    participant AI as AI Service
    participant KB as Knowledge Base
    participant MISTRAL as Mistral API

    User->>Frontend: Upload Resume
    Frontend->>Backend: POST /analyze
    Backend->>ORCH: orchestrate_analysis()

    ORCH->>RESUME: parse_resume()
    RESUME->>KB: lookup_skills()
    KB-->>RESUME: skill_definitions
    RESUME-->>ORCH: extracted_skills

    ORCH->>CAREER: analyze_career_gap(extracted_skills, target_role)
    CAREER->>KB: get_role_requirements(target_role)
    KB-->>CAREER: required_skills
    CAREER-->>ORCH: missing_skills, readiness_score

    ORCH->>ROADMAP: generate_roadmap(missing_skills)
    ROADMAP->>KB: get_prerequisites_and_order()
    KB-->>ROADMAP: ordered_skill_tree
    ROADMAP-->>ORCH: learning_steps

    ORCH->>REC: recommend_projects(missing_skills)
    REC->>KB: get_projects_for_skills()
    KB-->>REC: project_list
    REC-->>ORCH: recommendations

    ORCH->>AI: generate_explanations(results)
    AI->>MISTRAL: prompt(analysis_results)
    MISTRAL-->>AI: explanations
    AI-->>ORCH: ai_feedback

    ORCH-->>Backend: full_response
    Backend-->>Frontend: 200 OK
    Frontend-->>User: Dashboard with results