import os
import shutil
import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from schemas.schemas import MentorResponse
from utils.validators import sanitize_string, sanitize_filename, validate_skills_list, validate_career_goal, validate_study_hours

logger = logging.getLogger(__name__)
router = APIRouter()

_cache: Dict[str, dict] = {}
CACHE_TTL = 300

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _get_ai_service():
    from app.main import get_ai_service
    return get_ai_service()


def _get_orchestrator():
    from orchestrators.career_orchestrator import CareerOrchestrator  # pyrefly: ignore [missing-import]
    ai_svc = None
    try:
        from app.main import get_ai_service
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


@router.post("/career/explain")
async def explain_career(request: dict):
    career_goal = sanitize_string(request.get("career_goal", ""), max_length=100)
    user_skills = request.get("user_skills", [])

    if isinstance(user_skills, str):
        user_skills = [s.strip() for s in user_skills.split(",") if s.strip()]
    user_skills = validate_skills_list(user_skills)

    if not career_goal:
        raise HTTPException(status_code=400, detail="career_goal is required")

    try:
        ai_svc = _get_ai_service()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="AI service not available")

    orchestrator = _get_orchestrator()
    assessment, _ = orchestrator.analyze(user_skills, career_goal)

    text, confidence = await ai_svc.explain_career(assessment)
    return {"success": True, "data": {"explanation": text, "confidence": confidence}}


@router.post("/mentor/chat")
async def mentor_chat(request: dict):
    question = sanitize_string(request.get("question", ""), max_length=500)
    assessment_id = sanitize_string(request.get("assessment_id", ""), max_length=100)
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        ai_svc = _get_ai_service()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="AI service not available")

    from app.domain.models import Assessment as DomainAssessment, Career as DomainCareer, UserProfile as DomainUserProfile, Skill as DomainSkill
    from repositories.repositories import AssessmentRepository  # pyrefly: ignore [missing-import]
    from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]

    assessment = None
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
        except Exception as e:
            logger.warning("Failed to load assessment context from DB: %s", e)

    if not assessment:
        assessment = DomainAssessment(
            user_profile=DomainUserProfile(),
            target_career=DomainCareer(
                id="unknown", title="Unknown", description="", required_skills=[]
            ),
        )

    response = await ai_svc.mentor_chat(assessment, question)

    from schemas.schemas import MentorResponse  # pyrefly: ignore [missing-import]
    return MentorResponse(response=response)


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
