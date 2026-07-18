import os
import shutil
import logging
from typing import Dict

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import OperationalError

from utils.validators import sanitize_string, sanitize_filename, validate_skills_list, validate_career_goal, validate_study_hours

logger = logging.getLogger(__name__)
router = APIRouter()

_cache: Dict[str, dict] = {}
CACHE_TTL = 300

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _get_ai_service():
    from app.main import get_ai_service  # pyrefly: ignore [missing-import]
    return get_ai_service()


def _get_orchestrator():
    from orchestrators.career_orchestrator import CareerOrchestrator  # pyrefly: ignore [missing-import]
    ai_svc = None
    try:
        from app.main import get_ai_service  # pyrefly: ignore [missing-import]
        ai_svc = get_ai_service()
    except RuntimeError:
        pass
    return CareerOrchestrator(ai_service=ai_svc)


@router.get("/careers")
async def get_careers():
    from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
    roles = knowledge_loader.get_roles()
    return {
        "success": True,
        "data": [
            {"id": r["role"].lower().replace(" ", "-"), "title": r["role"], "description": r["description"]}
            for r in roles
        ],
    }


@router.get("/knowledge/skills")
async def get_skills():
    from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
    skills = knowledge_loader.get_skills()
    categories = {}
    for skill in skills:
        cat = skill.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill["name"])
    return {
        "success": True,
        "data": {
            "categories": [
                {"name": cat, "skills": skill_list}
                for cat, skill_list in categories.items()
            ],
        },
    }


@router.post("/career/analyze")
async def analyze_career(
    career_goal: str = Form(...),
    study_hours: int = Form(10),
    manual_skills: str = Form(None),
    resume: UploadFile = File(None),
):
    if not resume and not manual_skills:
        raise HTTPException(status_code=400, detail="Either resume or manual_skills is required")

    validated_goal = validate_career_goal(career_goal)
    if not validated_goal:
        raise HTTPException(status_code=400, detail=f"Invalid career goal: {career_goal}")

    study_hours = validate_study_hours(study_hours)

    extracted_skills = []
    if resume:
        ext = os.path.splitext(resume.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Use PDF, DOCX, or TXT.")

        if resume.size and resume.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")

        safe_filename = sanitize_filename(resume.filename or "upload")
        temp_dir = os.path.join(os.path.dirname(__file__), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, safe_filename)
        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)

            ai_svc = None
            try:
                ai_svc = _get_ai_service()
            except RuntimeError:
                pass

            from services.resume_service import ResumeService  # pyrefly: ignore [missing-import]
            resume_svc = ResumeService(ai_service=ai_svc)
            profile = resume_svc.parse(temp_file_path)
            extracted_skills = [s.name for s in profile.skills]
        except Exception as e:
            logger.error("Failed to parse resume: %s", e)
            raise HTTPException(status_code=500, detail=f"Failed to parse resume: {e}")
        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
    elif manual_skills:
        raw = [s.strip() for s in manual_skills.split(",") if s.strip()]
        extracted_skills = validate_skills_list(raw)

    if not extracted_skills:
        raise HTTPException(status_code=400, detail="No valid skills found in input")

    orchestrator = _get_orchestrator()
    result = await orchestrator.analyze_with_ai(
        user_skills=extracted_skills,
        career_goal=validated_goal,
        study_hours=study_hours,
    )

    return {"success": True, "data": result}


@router.post("/career/save")
async def save_assessment(request: dict):
    career_goal = sanitize_string(request.get("career_goal", ""), max_length=100)
    matched_skills = request.get("matched_skills", [])
    missing_skills = request.get("missing_skills", [])
    readiness_score = request.get("readiness_score", 0)
    roadmap = request.get("roadmap", [])
    estimated_weeks = request.get("estimated_weeks", 0)
    study_hours = request.get("study_hours", 10)

    if not career_goal:
        raise HTTPException(status_code=400, detail="career_goal is required")

    try:
        from repositories.repositories import AssessmentRepository, RoadmapRepository  # pyrefly: ignore [missing-import]
        assessment_repo = AssessmentRepository()
        roadmap_repo = RoadmapRepository()

        assessment = assessment_repo.create(
            user_id="00000000-0000-0000-0000-000000000001",
            career_goal=career_goal,
            readiness_score=readiness_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            weekly_hours=study_hours,
        )

        if roadmap:
            roadmap_repo.create(
                assessment_id=str(assessment.id),
                steps=roadmap,
                total_hours=sum(s.get("estimated_hours", 0) for s in roadmap),
                estimated_weeks=estimated_weeks,
            )

        return {
            "success": True,
            "data": {
                "assessment_id": str(assessment.id),
                "career_goal": career_goal,
                "readiness_score": readiness_score,
            },
        }
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database is unavailable. Please try again later.")
    except Exception as e:
        logger.warning("Failed to save assessment to DB: %s", e)
        raise HTTPException(status_code=500, detail="Failed to save assessment")


@router.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str):
    assessment_id = sanitize_string(assessment_id, max_length=100)
    if not assessment_id:
        raise HTTPException(status_code=400, detail="Invalid assessment ID")

    try:
        from repositories.repositories import AssessmentRepository, RoadmapRepository  # pyrefly: ignore [missing-import]
        from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
        assessment_repo = AssessmentRepository()
        roadmap_repo = RoadmapRepository()

        db_assess = assessment_repo.get_by_id(assessment_id)
        if not db_assess:
            raise HTTPException(status_code=404, detail="Assessment not found")

        role_data = knowledge_loader.get_role(str(db_assess.career_goal)) or {}

        matched = [str(n) for n in (db_assess.matched_skills or [])]
        missing = [str(n) for n in (db_assess.missing_skills or [])]

        roadmap_data: list = []
        db_roadmap = roadmap_repo.get_by_assessment(assessment_id)
        if db_roadmap:
            roadmap_data = db_roadmap.steps or []

        return {
            "success": True,
            "data": {
                "assessment_id": str(db_assess.id),
                "career_goal": str(db_assess.career_goal),
                "career_description": role_data.get("description", ""),
                "career_readiness": db_assess.readiness_score,
                "matched_skills": matched,
                "missing_skills": missing,
                "estimated_weeks": db_roadmap.estimated_weeks if db_roadmap else 0,
                "study_hours": db_assess.weekly_hours,
                "roadmap": roadmap_data,
                "created_at": str(db_assess.created_at) if db_assess.created_at else None,
            },
        }
    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database is unavailable. Please try again later.")
    except Exception as e:
        logger.warning("Failed to retrieve assessment: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment")


@router.post("/career/explain")
async def explain_career(request: dict):
    career_goal = sanitize_string(request.get("career_goal", ""), max_length=100)
    user_skills = request.get("user_skills", [])

    if isinstance(user_skills, str):
        user_skills = [s.strip() for s in user_skills.split(",") if s.strip()]
    user_skills = validate_skills_list(user_skills)

    if not career_goal:
        raise HTTPException(status_code=400, detail="career_goal is required")

    orchestrator = _get_orchestrator()
    assessment, _ = orchestrator.analyze(user_skills, career_goal)

    ai_svc = None
    try:
        ai_svc = _get_ai_service()
    except RuntimeError:
        pass

    if ai_svc:
        text, confidence = await ai_svc.explain_career(assessment)
    else:
        from ai.demo_data import get_demo_response
        text = get_demo_response("career")
        confidence = 0.5

    return {"success": True, "data": {"explanation": text, "confidence": confidence}}


@router.post("/mentor/chat")
async def mentor_chat(request: dict):
    question = sanitize_string(request.get("question", ""), max_length=500)
    assessment_id = sanitize_string(request.get("assessment_id", ""), max_length=100)
    session_id = sanitize_string(request.get("session_id", ""), max_length=100) or "default"
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    ai_svc = None
    try:
        ai_svc = _get_ai_service()
    except RuntimeError:
        pass

    from app.domain.models import Assessment as DomainAssessment, Career as DomainCareer, UserProfile as DomainUserProfile, Skill as DomainSkill
    from repositories.repositories import AssessmentRepository  # pyrefly: ignore [missing-import]
    from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]

    assessment = None
    knowledge_context = ""
    if assessment_id:
        try:
            repo = AssessmentRepository()
            db_assess = repo.get_by_id(assessment_id)
            if db_assess:
                role_data = knowledge_loader.get_role(db_assess.career_goal) or {}

                matched_names = db_assess.matched_skills or []
                missing_names = db_assess.missing_skills or []

                matched_skills = []
                for name in matched_names:
                    skill_data = knowledge_loader.get_skill(name) or {"name": name, "category": "", "difficulty": "intermediate"}
                    matched_skills.append(DomainSkill(**skill_data))

                missing_skills = []
                for name in missing_names:
                    skill_data = knowledge_loader.get_skill(name) or {"name": name, "category": "", "difficulty": "intermediate"}
                    missing_skills.append(DomainSkill(**skill_data))

                career = DomainCareer(
                    id=db_assess.career_goal.lower().replace(" ", "-"),
                    title=db_assess.career_goal,
                    description=role_data.get("description", ""),
                    required_skills=role_data.get("required_skills", []),
                )

                assessment = DomainAssessment(
                    user_profile=DomainUserProfile(skills=matched_skills),
                    target_career=career,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    readiness_score=db_assess.readiness_score,
                )

                cert_names = role_data.get("recommended_certifications", [])
                optional_skills = role_data.get("optional_skills", [])
                estimated_duration = role_data.get("estimated_duration", 0)

                cert_details = []
                for cn in cert_names[:5]:
                    cert_info = knowledge_loader.get_skill(cn) or {}
                    cert_details.append(f"- {cn}")

                knowledge_context = (
                    f"\n\nKnowledge Base Context:\n"
                    f"- Role Description: {role_data.get('description', '')}\n"
                    f"- All Required Skills: {role_data.get('required_skills', [])}\n"
                    f"- Optional Skills: {optional_skills}\n"
                    f"- Recommended Certifications: {cert_names}\n"
                    f"- Estimated Learning Duration: {estimated_duration} weeks\n"
                )

                for skill_name in missing_names[:5]:
                    skill_info = knowledge_loader.get_skill(skill_name)
                    if skill_info:
                        prereqs = skill_info.get("prerequisites", [])
                        category = skill_info.get("category", "")
                        difficulty = skill_info.get("difficulty", "")
                        knowledge_context += f"- Missing Skill '{skill_name}': category={category}, difficulty={difficulty}, prerequisites={prereqs}\n"
        except Exception as e:
            logger.warning("Failed to load assessment context from DB: %s", e)

    if not assessment:
        all_roles = knowledge_loader.get_roles()
        role_list = [r.get("role", "") for r in all_roles]
        knowledge_context = (
            f"\n\nKnowledge Base Context:\n"
            f"- Available Career Paths: {role_list}\n"
            f"- The user has not completed an assessment yet.\n"
        )

    if ai_svc:
        response = await ai_svc.mentor_chat(
            assessment, question,
            session_id=session_id,
            knowledge_context=knowledge_context,
        )
    else:
        from ai.demo_data import get_demo_response
        response = get_demo_response("mentor", question=question)

    return {"success": True, "response": response}


@router.delete("/mentor/session/{session_id}")
async def clear_mentor_session(session_id: str):
    try:
        ai_svc = _get_ai_service()
        ai_svc.clear_session(session_id)
    except RuntimeError:
        pass
    return {"success": True, "message": "Session cleared"}


@router.get("/projects")
async def get_projects():
    from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
    projects = knowledge_loader.get_projects()
    return {"success": True, "data": projects}


@router.get("/projects/{skill_name}")
async def get_projects_for_skill(skill_name: str):
    from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
    projects = knowledge_loader.get_projects_for_skill(skill_name)
    return {"success": True, "data": projects}


@router.get("/certifications/{role_name}")
async def get_certifications_for_role(role_name: str):
    from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
    certs = knowledge_loader.get_certifications_for_role(role_name)
    return {"success": True, "data": certs}


@router.get("/learning-paths/{career}")
async def get_learning_path(career: str):
    from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
    path = knowledge_loader.get_learning_path(career)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return {"success": True, "data": path}


@router.get("/resources/{skill_name}")
async def get_skill_resources(skill_name: str):
    skill_name = sanitize_string(skill_name, max_length=100)
    if not skill_name:
        raise HTTPException(status_code=400, detail="Invalid skill name")
    from knowledge.resources import get_free_resources  # pyrefly: ignore [missing-import]
    resources = get_free_resources(skill_name)
    return {"success": True, "data": resources}
