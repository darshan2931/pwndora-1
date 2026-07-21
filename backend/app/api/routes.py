import os
import logging
import datetime

from fastapi import APIRouter, File, Form, UploadFile, Depends
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy import select

from utils.validators import sanitize_string, sanitize_filename, validate_skills_list, validate_career_goal, validate_study_hours
from app.api.deps import get_current_user
from models.sqlalchemy_models import User, ChatMemory
from database.session import get_db, SessionLocal
from app.api.auth import router as auth_router
from core.errors import (
    ErrorCode, error_response, validation_error, not_found, forbidden,
    unauthorized, ai_unavailable, ai_error, database_error, file_too_large,
    unsupported_file_type, internal_error,
)

logger = logging.getLogger(__name__)
router = APIRouter()
router.include_router(auth_router)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

RESOURCE_ENRICHMENT = {
    "Microsoft Learn": {"url": "https://learn.microsoft.com/en-us/windows/", "type": "course", "free": True},
    "Splunk Free Training": {"url": "https://www.splunk.com/en_us/training/free-online-training.html", "type": "course", "free": True},
    "Splunk Documentation": {"url": "https://docs.splunk.com/", "type": "article", "free": True},
    "Wireshark Documentation": {"url": "https://www.wireshark.org/docs/", "type": "article", "free": True},
    "Wireshark Wiki": {"url": "https://wiki.wireshark.org/", "type": "article", "free": True},
    "Cisco Skills for All": {"url": "https://skillsforall.com/", "type": "course", "free": True},
    "TryHackMe": {"url": "https://tryhackme.com/", "type": "lab", "free": True},
    "Hack The Box": {"url": "https://www.hackthebox.com/", "type": "lab", "free": True},
    "SANS DFIR": {"url": "https://www.sans.org/white-papers/incident-handling-process/", "type": "article", "free": True},
    "Automate the Boring Stuff": {"url": "https://automatetheboringstuff.com/", "type": "book", "free": True},
    "MITRE ATT&CK Website": {"url": "https://attack.mitre.org/", "type": "article", "free": True},
    "The Linux Command Line": {"url": "https://linuxcommand.org/tlcl.php", "type": "book", "free": True},
    "OverTheWire": {"url": "https://overthewire.org/wargames/bandit/", "type": "lab", "free": True},
    "Nmap Documentation": {"url": "https://nmap.org/docs.html", "type": "article", "free": True},
    "PortSwigger Web Security Academy": {"url": "https://portswigger.net/web-security", "type": "course", "free": True},
    "PortSwigger": {"url": "https://portswigger.net/web-security", "type": "course", "free": True},
    "DFIR Training": {"url": "https://www.dfir.training/", "type": "course", "free": True},
    "Kubernetes Documentation": {"url": "https://kubernetes.io/docs/home/", "type": "article", "free": True},
    "HashiCorp Learn": {"url": "https://developer.hashicorp.com/terraform/tutorials", "type": "course", "free": True},
    "AWS Documentation": {"url": "https://docs.aws.amazon.com/iam/", "type": "article", "free": True},
    "OWASP": {"url": "https://owasp.org/www-project-top-ten/", "type": "article", "free": True},
    "Splunk": {"url": "https://www.splunk.com/en_us/training/free-online-training.html", "type": "course", "free": True},
    "Wireshark": {"url": "https://www.wireshark.org/docs/", "type": "article", "free": True},
    "CompTIA Security+": {"url": "https://www.comptia.org/certifications/security", "type": "course", "free": False},
    "Google Cybersecurity Professional Certificate": {"url": "https://www.coursera.org/professional-certificates/google-cybersecurity", "type": "course", "free": False},
    "Blue Team Level 1": {"url": "https://securityblue.team/bugs/", "type": "course", "free": False},
    "eJPT": {"url": "https://ine.com/certifications/ine-security-certified-endpoint-professional", "type": "course", "free": False},
    "PNPT": {"url": "https://pntoacademy.com/pnpt", "type": "course", "free": False},
    "OSCP": {"url": "https://www.offensive-security.com/pwk-oscp/", "type": "course", "free": False},
    "AWS Security Specialty": {"url": "https://aws.amazon.com/certification/certified-security-specialty/", "type": "course", "free": False},
    "CCSK": {"url": "https://cloudsecurityalliance.org/research/ccsk/", "type": "course", "free": False},
    "Azure Security Engineer": {"url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-security-engineer/", "type": "course", "free": False},
    "CSSLP": {"url": "https://www.isc2.org/credentials/csslp", "type": "course", "free": False},
    "GCFA": {"url": "https://www.giac.org/certifications/forensic-analyst-gcfa/", "type": "course", "free": False},
    "CTIA": {"url": "https://cert.eccouncil.org/programs/cyber-threat-intelligence-ctia/", "type": "course", "free": False},
    "GCTI": {"url": "https://www.giac.org/certifications/cyber-threat-intelligence-gcti/", "type": "course", "free": False},
    "CISSP": {"url": "https://www.isc2.org/credentials/cissp", "type": "course", "free": False},
    "CCSP": {"url": "https://www.isc2.org/credentials/ccsp", "type": "course", "free": False},
    "Certified Kubernetes Security Specialist": {"url": "https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/", "type": "course", "free": False},
    "GCIH": {"url": "https://www.giac.org/certifications/incident-handler-gcih/", "type": "course", "free": False},
    "CISA": {"url": "https://www.isaca.org/credentials/cisa", "type": "course", "free": False},
    "CRISC": {"url": "https://www.isaca.org/credentials/crisc", "type": "course", "free": False},
    "ISO 27001 Lead Implementer": {"url": "https://pecb.com/en/education-and-certification-for-individuals/iso-27001-lead-implementer", "type": "course", "free": False},
    "CEH": {"url": "https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/", "type": "course", "free": False},
    "CompTIA CySA+": {"url": "https://www.comptia.org/certifications/cybersecurity-analyst", "type": "course", "free": False},
    "OSWE": {"url": "https://www.offensive-security.com/awe-oswe/", "type": "course", "free": False},
}


def _enrich_resource(r: dict, step_idx: int, res_idx: int) -> dict:
    """Enrich a resource with proper URL, type, and free status from the enrichment map."""
    title = r.get("title", "")
    enriched = RESOURCE_ENRICHMENT.get(title, {})
    return {
        "id": r.get("id", f"res-{step_idx}-{res_idx}"),
        "title": title,
        "type": enriched.get("type", r.get("type", "article")),
        "url": enriched.get("url", r.get("url", "#")),
        "free": enriched.get("free", r.get("free", True)),
    }


def _normalize_roadmap_steps(steps: list) -> list:
    """Convert old-format roadmap steps to the RoadmapNode format expected by the frontend."""
    normalized = []
    total = len(steps)
    for i, step in enumerate(steps):
        if "title" in step and "status" in step and "type" in step:
            step["completedAt"] = step.get("completedAt", step.get("completed_at"))
            step["resources"] = [_enrich_resource(r, i, j) for j, r in enumerate(step.get("resources", []))]
            normalized.append(step)
            continue

        skill_name = step.get("skill", "Unknown")
        if i == 0:
            status = "in-progress"
        elif i == 1:
            status = "available"
        else:
            status = "locked"

        resources = []
        for j, r in enumerate(step.get("resources", [])):
            if isinstance(r, str):
                resources.append(_enrich_resource({"title": r}, i, j))
            elif isinstance(r, dict):
                resources.append(_enrich_resource(r, i, j))

        normalized.append({
            "id": step.get("id", f"step-{i}"),
            "title": skill_name,
            "description": step.get("description", f"Learn {skill_name}"),
            "type": step.get("type", "skill"),
            "status": step.get("status", status),
            "estimatedHours": step.get("estimated_hours", step.get("estimatedHours", 10)),
            "difficulty": step.get("difficulty", "Beginner"),
            "skills": step.get("skills", [skill_name]),
            "prerequisites": step.get("prerequisites", []),
            "resources": resources,
            "completedAt": step.get("completedAt", step.get("completed_at")),
        })
    return normalized


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




@router.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str, current_user: User = Depends(get_current_user)):
    assessment_id = sanitize_string(assessment_id, max_length=100)
    if not assessment_id:
        validation_error("Invalid assessment ID")

    try:
        from repositories.repositories import AssessmentRepository, RoadmapRepository  # pyrefly: ignore [missing-import]
        from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
        assessment_repo = AssessmentRepository()
        roadmap_repo = RoadmapRepository()

        db_assess = assessment_repo.get_by_id(assessment_id)
        if not db_assess:
            not_found("Assessment not found")

        if str(db_assess.user_id) != str(current_user.id):
            forbidden("Not authorized to view this assessment")

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
    except OperationalError:
        database_error()
    except Exception as e:
        logger.warning("Failed to retrieve assessment: %s", e)
        internal_error("Failed to retrieve assessment")


@router.post("/career/analyze")
async def analyze_career(
    career_goal: str = Form(...),
    study_hours: int = Form(10),
    manual_skills: str = Form(None),
    resume: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
):
    if not resume and not manual_skills:
        validation_error("Either resume or manual_skills is required")

    validated_goal = validate_career_goal(career_goal)
    if not validated_goal:
        validation_error(f"Invalid career goal: {career_goal}")

    study_hours = validate_study_hours(study_hours)

    extracted_skills = []
    if resume:
        ext = os.path.splitext(resume.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            unsupported_file_type(ext)

        if resume.size and resume.size > MAX_FILE_SIZE:
            file_too_large()

        from services.storage_service import StorageService
        storage = StorageService()
        temp_file_path = storage.save_upload(resume)

        try:
            ai_svc = None
            try:
                ai_svc = _get_ai_service()
            except RuntimeError:
                pass

            from services.resume_service import ResumeService  # pyrefly: ignore [missing-import]
            resume_svc = ResumeService(ai_service=ai_svc)
            profile = await resume_svc.parse_async(temp_file_path)
            extracted_skills = [s.name for s in profile.skills]
        except Exception as e:
            logger.error("Failed to parse resume: %s", e)
            internal_error("Failed to parse resume")
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass
    elif manual_skills:
        raw = [s.strip() for s in manual_skills.split(",") if s.strip()]
        extracted_skills = validate_skills_list(raw)

    if not extracted_skills:
        validation_error("No valid skills found in input")

    orchestrator = _get_orchestrator()
    result = await orchestrator.analyze_with_ai(
        user_skills=extracted_skills,
        career_goal=validated_goal,
        study_hours=study_hours,
    )

    return {"success": True, "data": result}


@router.post("/career/save")
async def save_assessment(request: dict, current_user: User = Depends(get_current_user)):
    career_goal = sanitize_string(request.get("career_goal", ""), max_length=100)
    matched_skills = request.get("matched_skills", [])
    missing_skills = request.get("missing_skills", [])
    readiness_score = request.get("readiness_score", 0)
    roadmap = request.get("roadmap", [])
    estimated_weeks = request.get("estimated_weeks", 0)
    study_hours = request.get("study_hours", 10)
    learning_preferences = request.get("learning_preferences", [])

    if not career_goal:
        validation_error("career_goal is required")

    try:
        from repositories.repositories import AssessmentRepository, RoadmapRepository  # pyrefly: ignore [missing-import]
        assessment_repo = AssessmentRepository()
        roadmap_repo = RoadmapRepository()

        assessment = assessment_repo.create(
            user_id=str(current_user.id),
            career_goal=career_goal,
            readiness_score=readiness_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            weekly_hours=study_hours,
            learning_preferences=learning_preferences,
        )

        if roadmap:
            total_hours = sum(s.get("estimatedHours", s.get("estimated_hours", 0)) for s in roadmap)
            roadmap_repo.create(
                assessment_id=str(assessment.id),
                steps=roadmap,
                total_hours=total_hours,
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
        database_error()
    except Exception as e:
        logger.warning("Failed to save assessment to DB: %s", e)
        internal_error("Failed to save assessment")





@router.get("/mentor/greeting")
async def get_mentor_greeting(current_user: User = Depends(get_current_user)):
    from repositories.repositories import AssessmentRepository, RoadmapRepository
    from app.ai.context_builder import ContextBuilder
    
    assessment_repo = AssessmentRepository()
    roadmap_repo = RoadmapRepository()
    
    # Get latest assessment
    db_assess = assessment_repo.get_by_user_id(str(current_user.id))
    if not db_assess:
        db_assess = None
    else:
        # get_by_user_id might return a list, take first or sort
        if isinstance(db_assess, list):
            db_assess = db_assess[0] if db_assess else None
            
    if not db_assess:
        return {"success": True, "greeting": "Welcome to Cyber Mentor! Please initialize your profile first by uploading your resume."}
        
    db_roadmap = roadmap_repo.get_by_assessment(str(db_assess.id))
    context_str = ContextBuilder.build_mentor_context(current_user, db_assess, db_roadmap)
    
    try:
        ai_svc = _get_ai_service()
        greeting = await ai_svc.generate_proactive_greeting(context_str)
        return {"success": True, "greeting": greeting}
    except Exception as e:
        logger.warning(f"Failed to generate greeting: {e}")
        return {"success": True, "greeting": "Hello! I am ready to help you with your cybersecurity career. What would you like to focus on today?"}


@router.post("/mentor/chat")
async def mentor_chat(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = sanitize_string(request.get("question", ""), max_length=500)
    session_id = sanitize_string(request.get("session_id", ""), max_length=100) or "default"
    if not question:
        validation_error("Question is required")

    ai_svc = None
    try:
        ai_svc = _get_ai_service()
    except RuntimeError:
        ai_unavailable("AI Mentor service is not configured.")

    from repositories.repositories import AssessmentRepository, RoadmapRepository
    from app.ai.context_builder import ContextBuilder
    
    assessment_repo = AssessmentRepository()
    roadmap_repo = RoadmapRepository()
    
    db_assess = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(db_assess, list):
        db_assess = db_assess[0] if db_assess else None
        
    context_str = ""
    if db_assess:
        db_roadmap = roadmap_repo.get_by_assessment(str(db_assess.id))
        context_str = ContextBuilder.build_mentor_context(current_user, db_assess, db_roadmap)

    # 1. Fetch latest memory
    db_memory = db.scalars(
        select(ChatMemory)
        .filter_by(user_id=str(current_user.id), session_id=session_id)
        .order_by(ChatMemory.created_at.desc())
    ).first()
    
    history = []
    if db_memory:
        history.append({"role": "system", "content": f"Previous conversation summary: {db_memory.summary}"})
        if db_memory.important_facts:
            facts = ", ".join(db_memory.important_facts)
            history.append({"role": "system", "content": f"Important facts: {facts}"})
        if db_memory.next_goal:
            history.append({"role": "system", "content": f"User's next goal: {db_memory.next_goal}"})

    # 2. Get AI response
    try:
        response = await ai_svc.mentor_chat(
            question=question,
            context=context_str,
            session_id=session_id,
            history=history,
        )
    except RuntimeError as e:
        logger.warning("Mentor chat AI failed: %s", e)
        ai_unavailable("AI Mentor service is currently unavailable.")

    # 3. Summarize the new turn + history
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response})
    
    try:
        summary_data = await ai_svc.summarize_session(history, session_id)
        
        if isinstance(summary_data, str):
            summary_data = {"summary": summary_data, "important_facts": [], "next_goal": ""}

        # 4. Save to DB
        new_memory = ChatMemory(
            user_id=str(current_user.id),
            session_id=session_id,
            summary=summary_data.get("summary", ""),
            important_facts=summary_data.get("important_facts", []),
            next_goal=summary_data.get("next_goal", "")
        )
        db.add(new_memory)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to summarize and save session: {e}")
        # Even if summary fails, we still return the response to the user

    return {"success": True, "response": response}


@router.delete("/mentor/session/{session_id}")
async def clear_mentor_session(session_id: str, current_user: User = Depends(get_current_user)):
    session_id = sanitize_string(session_id, max_length=100)
    try:
        ai_svc = _get_ai_service()
        ai_svc.clear_session(session_id)
    except RuntimeError:
        pass
    return {"success": True, "message": "Session cleared"}



@router.get("/resources/{skill_name}")
async def get_skill_resources(skill_name: str, current_user: User = Depends(get_current_user)):
    skill_name = sanitize_string(skill_name, max_length=100)
    if not skill_name:
        validation_error("Invalid skill name")
    from knowledge.resources import get_free_resources  # pyrefly: ignore [missing-import]
    resources = get_free_resources(skill_name)
    return {"success": True, "data": resources}


@router.post("/resume-review/upload")
async def upload_resume_review(
    career_goal: str = Form(...),
    resume: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not career_goal:
        validation_error("Career goal is required")

    ext = os.path.splitext(resume.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        unsupported_file_type(ext)

    if resume.size and resume.size > MAX_FILE_SIZE:
        file_too_large()

    temp_file_path = None
    try:
        from services.storage_service import StorageService
        storage = StorageService()
        temp_file_path = storage.save_upload(resume)

        # 1. Extract text from resume
        ai_svc = _get_ai_service()
        from services.resume_service import ResumeService  # pyrefly: ignore [missing-import]
        resume_svc = ResumeService(ai_service=ai_svc)
        text = await resume_svc.extract_text(temp_file_path)

        # 2. Get AI feedback
        feedback = await ai_svc.review_resume(text, career_goal)

        # 3. Save to DB
        from repositories.repositories import ResumeReviewRepository  # pyrefly: ignore [missing-import]
        repo = ResumeReviewRepository()
        review = repo.create(
            user_id=str(current_user.id),
            career_goal=career_goal,
            feedback=feedback
        )

        return {
            "success": True, 
            "data": {
                "id": str(review.id),
                "career_goal": review.career_goal,
                "feedback": review.feedback,
                "created_at": str(review.created_at)
            }
        }
    except Exception as e:
        logger.error("Failed to process resume review: %s", e)
        internal_error("Failed to process resume review")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass


@router.get("/resume-review")
async def get_resume_reviews(current_user: User = Depends(get_current_user)):
    from repositories.repositories import ResumeReviewRepository  # pyrefly: ignore [missing-import]
    repo = ResumeReviewRepository()
    reviews = repo.get_by_user_id(str(current_user.id))
    
    return {
        "success": True,
        "data": [
            {
                "id": str(r.id),
                "career_goal": r.career_goal,
                "feedback": r.feedback,
                "created_at": str(r.created_at)
            }
            for r in reviews
        ]
    }


@router.post("/resume/profile/analyze")
async def analyze_resume_profile(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    from services.resume_text_extractor import ResumeTextExtractor
    from services.resume_profile_service import ResumeProfileService
    from repositories.repositories import ResumeProfileRepository

    repo = ResumeProfileRepository()
    temp_file_path = None

    try:
        file_size = file.size if hasattr(file, 'size') else None
        ext = ResumeTextExtractor.validate_file(file.filename, file_size)

        from services.storage_service import StorageService
        storage = StorageService()
        temp_file_path = storage.save_upload(file)

        actual_size = os.path.getsize(temp_file_path)

        db_profile = repo.create(
            user_id=str(current_user.id),
            original_filename=os.path.basename(file.filename or "unknown"),
            file_type=ext.lstrip("."),
            file_size=actual_size,
        )
        profile_id = str(db_profile.id)

        repo.update_status(profile_id, "extracting")

        extraction = ResumeTextExtractor.extract(temp_file_path)

        repo.update_status(profile_id, "analyzing")

        from services.resume_url_extractor import ResumeURLExtractor
        urls = ResumeURLExtractor.extract(extraction.text)

        ai_svc = None
        try:
            ai_svc = _get_ai_service()
        except Exception:
            pass

        profile_svc = ResumeProfileService(ai_service=ai_svc)
        profile_data = await profile_svc._extract_profile_with_ai(extraction.text)

        profile_dict = profile_data.model_dump() if profile_data else {}

        repo.update_result(
            profile_id=profile_id,
            extracted_profile=profile_dict,
            extracted_urls=urls,
            raw_text=extraction.text[:50000],
        )

        return {
            "success": True,
            "data": {
                "id": profile_id,
                "status": "completed",
                "profile": profile_dict,
                "urls": urls,
                "metadata": {
                    "file_type": extraction.file_type,
                    "character_count": extraction.character_count,
                    "page_count": extraction.page_count,
                },
            },
        }

    except ValueError as e:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass
        if 'profile_id' in dir():
            repo.update_status(str(profile_id), "failed", str(e))
        validation_error(str(e))
    except Exception as e:
        logger.error("Resume profile analysis failed: %s", e)
        if 'profile_id' in dir():
            try:
                repo.update_status(str(profile_id), "failed", str(e))
            except Exception:
                pass
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass
        internal_error("Failed to analyze resume profile")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass


@router.get("/resume/profile")
async def get_resume_profile(current_user: User = Depends(get_current_user)):
    from repositories.repositories import ResumeProfileRepository

    repo = ResumeProfileRepository()
    profile = repo.get_latest_by_user_id(str(current_user.id))

    if not profile:
        return {
            "success": True,
            "data": None,
        }

    return {
        "success": True,
        "data": {
            "id": str(profile.id),
            "status": profile.processing_status,
            "profile": profile.extracted_profile or {},
            "urls": profile.extracted_urls or {},
            "metadata": {
                "file_type": profile.file_type,
                "character_count": len(profile.raw_text) if profile.raw_text else 0,
                "original_filename": profile.original_filename,
                "file_size": profile.file_size,
            },
            "error": profile.processing_error,
            "created_at": str(profile.created_at) if profile.created_at else None,
        },
    }


@router.post("/github/analyze")
async def analyze_github(
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user),
):
    from repositories.repositories import ResumeProfileRepository, GitHubProfileRepository, GitHubRepositoryEvidenceRepository
    from services.github_url_parser import GitHubURLParser
    from services.github_evidence_service import GitHubEvidenceService

    resume_repo = ResumeProfileRepository()
    gh_profile_repo = GitHubProfileRepository()
    gh_evidence_repo = GitHubRepositoryEvidenceRepository()

    resume_profile = resume_repo.get_latest_by_user_id(str(current_user.id))
    if not resume_profile:
        validation_error("No resume profile found. Upload a resume first.")

    urls = resume_profile.extracted_urls or {}
    github_urls = urls.get("github", [])
    if not github_urls:
        return {
            "success": True,
            "data": {
                "status": "no_github_profile",
                "message": "No GitHub profile was detected in the uploaded resume.",
            },
        }

    github_url = github_urls[0]
    parsed = GitHubURLParser.parse(github_url)
    if not parsed:
        return {
            "success": True,
            "data": {
                "status": "invalid_github_url",
                "message": f"Could not extract a valid GitHub username from: {github_url}",
            },
        }

    ai_svc = None
    try:
        ai_svc = _get_ai_service()
    except Exception:
        pass

    service = GitHubEvidenceService(ai_service=ai_svc)

    existing_gh = gh_profile_repo.get_latest_by_user_id(str(current_user.id))
    if existing_gh and existing_gh.username == parsed["username"] and existing_gh.processing_status == "completed":
        if not force_refresh:
            gh_evidence_items = gh_evidence_repo.get_by_profile_id(str(existing_gh.id))
            return {
                "success": True,
                "data": {
                    "status": "completed",
                    "username": existing_gh.username,
                    "profile_url": existing_gh.profile_url,
                    "avatar_url": existing_gh.avatar_url,
                    "public_repositories": existing_gh.public_repositories,
                    "followers": existing_gh.followers,
                    "following": existing_gh.following,
                    "repositories_analyzed": len(gh_evidence_items),
                    "fetched_at": str(existing_gh.fetched_at) if existing_gh.fetched_at else None,
                    "cached": True,
                },
            }

    if existing_gh:
        gh_profile_id = str(existing_gh.id)
        gh_profile_repo.update_status(gh_profile_id, "analyzing")
        gh_evidence_repo.delete_by_profile_id(gh_profile_id)
    else:
        new_gh = gh_profile_repo.create(
            user_id=str(current_user.id),
            username=parsed["username"],
            profile_url=parsed["profile_url"],
            resume_profile_id=str(resume_profile.id),
        )
        gh_profile_id = str(new_gh.id)
        gh_profile_repo.update_status(gh_profile_id, "analyzing")

    try:
        result = await service.analyze(
            github_url=github_url,
            resume_profile_id=str(resume_profile.id),
            user_id=str(current_user.id),
            force_refresh=force_refresh,
        )

        if result.status != "completed":
            gh_profile_repo.update_status(gh_profile_id, "failed", result.message)
            return {
                "success": True,
                "data": {
                    "status": result.status,
                    "message": result.message,
                },
            }

        gp = result.github_profile
        gh_profile_repo.update_result(
            gh_profile_id,
            avatar_url=gp.avatar_url if gp else None,
            public_repositories=gp.public_repositories if gp else 0,
            followers=gp.followers if gp else 0,
            following=gp.following if gp else 0,
            account_created_at=gp.account_created_at if gp else None,
            fetched_at=datetime.datetime.now(datetime.timezone.utc),
            processing_status="completed",
        )

        repo_items = []
        for repo_ev in result.repositories:
            repo_items.append({
                "repository_name": repo_ev.repository.name,
                "full_name": repo_ev.repository.full_name,
                "description": repo_ev.repository.description,
                "repository_url": repo_ev.repository.html_url,
                "languages": repo_ev.repository.languages,
                "topics": repo_ev.repository.topics,
                "readme_text": repo_ev.readme.readme_text if repo_ev.readme else None,
                "readme_available": 1 if (repo_ev.readme and repo_ev.readme.readme_available) else 0,
                "stars": repo_ev.repository.stars,
                "forks": repo_ev.repository.forks,
                "is_fork": 1 if repo_ev.repository.is_fork else 0,
                "is_archived": 1 if repo_ev.repository.is_archived else 0,
                "created_at_github": repo_ev.repository.created_at,
                "updated_at_github": repo_ev.repository.updated_at,
                "pushed_at_github": repo_ev.repository.pushed_at,
                "selection_reasons": repo_ev.repository.selection_reasons,
                "ai_analysis": repo_ev.ai_analysis.model_dump() if repo_ev.ai_analysis else {},
                "tech_evidence": [t.model_dump() for t in repo_ev.tech_evidence],
            })
        if repo_items:
            gh_evidence_repo.create_many(gh_profile_id, repo_items)

        return {
            "success": True,
            "data": {
                "status": "completed",
                "username": gp.username if gp else parsed["username"],
                "profile_url": gp.profile_url if gp else parsed["profile_url"],
                "avatar_url": gp.avatar_url if gp else None,
                "public_repositories": gp.public_repositories if gp else 0,
                "followers": gp.followers if gp else 0,
                "following": gp.following if gp else 0,
                "repositories_analyzed": result.repositories_analyzed,
                "all_technologies": [t.model_dump() for t in result.all_technologies],
                "repositories": [
                    {
                        "name": r.repository.name,
                        "full_name": r.repository.full_name,
                        "description": r.repository.description,
                        "html_url": r.repository.html_url,
                        "stars": r.repository.stars,
                        "forks": r.repository.forks,
                        "topics": r.repository.topics,
                        "languages": r.repository.languages,
                        "has_readme": r.repository.has_readme,
                        "selection_reasons": r.repository.selection_reasons,
                        "ai_analysis": r.ai_analysis.model_dump() if r.ai_analysis else None,
                    }
                    for r in result.repositories
                ],
                "cached": False,
            },
        }

    except Exception as e:
        logger.error("GitHub analysis failed: %s", e)
        gh_profile_repo.update_status(gh_profile_id, "failed", str(e))
        internal_error("GitHub analysis failed. Please try again later.")


@router.get("/github/profile")
async def get_github_profile(current_user: User = Depends(get_current_user)):
    from repositories.repositories import GitHubProfileRepository, GitHubRepositoryEvidenceRepository

    gh_profile_repo = GitHubProfileRepository()
    gh_evidence_repo = GitHubRepositoryEvidenceRepository()

    profile = gh_profile_repo.get_latest_by_user_id(str(current_user.id))
    if not profile:
        return {
            "success": True,
            "data": None,
        }

    repo_evidences = gh_evidence_repo.get_by_profile_id(str(profile.id))

    return {
        "success": True,
        "data": {
            "username": profile.username,
            "profile_url": profile.profile_url,
            "avatar_url": profile.avatar_url,
            "public_repositories": profile.public_repositories,
            "followers": profile.followers,
            "following": profile.following,
            "account_created_at": profile.account_created_at,
            "fetched_at": str(profile.fetched_at) if profile.fetched_at else None,
            "repositories_analyzed": len(repo_evidences),
            "processing_status": profile.processing_status,
            "processing_error": profile.processing_error,
            "created_at": str(profile.created_at) if profile.created_at else None,
            "repositories": [
                {
                    "name": r.repository_name,
                    "full_name": r.full_name,
                    "description": r.description,
                    "html_url": r.repository_url,
                    "stars": r.stars,
                    "forks": r.forks,
                    "topics": r.topics or [],
                    "languages": r.languages or {},
                    "has_readme": bool(r.readme_available),
                    "selection_reasons": r.selection_reasons or [],
                    "ai_analysis": r.ai_analysis or {},
                }
                for r in repo_evidences
            ],
        },
    }


@router.get("/github/evidence")
async def get_github_evidence(current_user: User = Depends(get_current_user)):
    from repositories.repositories import GitHubProfileRepository, GitHubRepositoryEvidenceRepository

    gh_profile_repo = GitHubProfileRepository()
    gh_evidence_repo = GitHubRepositoryEvidenceRepository()

    profile = gh_profile_repo.get_latest_by_user_id(str(current_user.id))
    if not profile or profile.processing_status != "completed":
        return {
            "success": True,
            "data": {
                "evidence": [],
                "repositories_analyzed": 0,
            },
        }

    repo_evidences = gh_evidence_repo.get_by_profile_id(str(profile.id))

    all_evidence = []
    for r in repo_evidences:
        if r.tech_evidence:
            all_evidence.extend(r.tech_evidence)

    deduped = {}
    for ev in all_evidence:
        if isinstance(ev, dict):
            key = f"{ev.get('technology', '')}:{ev.get('evidence_type', '')}:{ev.get('repository', '')}"
            if key not in deduped:
                deduped[key] = ev

    return {
        "success": True,
        "data": {
            "evidence": list(deduped.values()),
            "repositories_analyzed": len(repo_evidences),
        },
    }


@router.post("/roadmap/{roadmap_id}/step/{step_index}/toggle")
async def toggle_roadmap_step(
    roadmap_id: str, 
    step_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from repositories.repositories import RoadmapRepository, AssessmentRepository  # pyrefly: ignore [missing-import]
    from models.sqlalchemy_models import Roadmap
    roadmap_repo = RoadmapRepository()
    
    roadmap = roadmap_repo.get_by_assessment(roadmap_id)
    if not roadmap:
        roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
        if not roadmap:
            not_found("Roadmap not found")

    assessment_repo = AssessmentRepository()
    user_assessments = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(user_assessments, list):
        user_assessment_ids = {str(a.id) for a in user_assessments}
    else:
        user_assessment_ids = {str(user_assessments.id)} if user_assessments else set()
    
    if str(roadmap.assessment_id) not in user_assessment_ids and str(roadmap.id) not in user_assessment_ids:
        forbidden("You do not have permission to modify this roadmap")

    steps = _normalize_roadmap_steps(list(roadmap.steps))
    
    if step_index < 0 or step_index >= len(steps):
        validation_error("Invalid step index")
        
    current_status = steps[step_index].get("status", "available")
    
    if current_status == "available":
        steps[step_index]["status"] = "in-progress"
    elif current_status == "in-progress":
        steps[step_index]["status"] = "completed"
        steps[step_index]["completed_at"] = str(datetime.datetime.now())
        
        # Unlock the next step if it exists and is locked
        if step_index + 1 < len(steps) and steps[step_index + 1].get("status") == "locked":
            steps[step_index + 1]["status"] = "available"
    elif current_status == "completed":
        steps[step_index]["status"] = "in-progress"
        steps[step_index]["completed_at"] = None
    
    updated_roadmap = roadmap_repo.update_steps(str(roadmap.id), steps)
    
    return {
        "success": True,
        "data": {
            "roadmap_id": str(updated_roadmap.id),
            "steps": updated_roadmap.steps
        }
    }


@router.get("/career/dashboard")
async def get_dashboard(current_user: User = Depends(get_current_user)):
    from repositories.repositories import AssessmentRepository, RoadmapRepository
    from knowledge.loader import knowledge_loader
    from datetime import datetime, timedelta
    
    assessment_repo = AssessmentRepository()
    roadmap_repo = RoadmapRepository()
    
    # Get latest assessment
    db_assess = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(db_assess, list):
        db_assess = db_assess[0] if db_assess else None
        
    if not db_assess:
        # User hasn't onboarded yet
        return {"success": True, "data": None}
        
    db_roadmap = roadmap_repo.get_by_assessment(str(db_assess.id))
    roadmap_steps = _normalize_roadmap_steps(db_roadmap.steps if db_roadmap else [])
    
    # Build Profile
    role_data = knowledge_loader.get_role(str(db_assess.career_goal)) or {}
    
    # Format skills to frontend Skill interface
    known = [{"id": s, "name": s, "category": "Skill", "confirmed": True, "level": "beginner"} for s in (db_assess.matched_skills or [])]
    missing = [{"id": s, "name": s, "category": "Skill", "confirmed": False, "level": "beginner"} for s in (db_assess.missing_skills or [])]
    
    roadmap_progress = 0
    if roadmap_steps:
        completed = sum(1 for s in roadmap_steps if s.get("status") == "completed")
        roadmap_progress = int((completed / len(roadmap_steps)) * 100)
        
    current_streak = 3  # Hardcoded for demo gamification purposes
    achievements = []
    
    if current_streak >= 3:
        achievements.append({
            "id": "consistency_rookie",
            "title": "Consistency Rookie",
            "description": "Maintained a 3-day learning streak.",
            "icon": "Flame",
            "unlockedAt": str(datetime.utcnow())
        })
    if current_streak >= 7:
        achievements.append({
            "id": "cyber_scholar",
            "title": "Cyber Scholar",
            "description": "Maintained a 7-day learning streak.",
            "icon": "Star",
            "unlockedAt": str(datetime.utcnow())
        })
    if roadmap_progress == 100:
        achievements.append({
            "id": "pathfinder",
            "title": "Pathfinder",
            "description": "Completed an entire learning roadmap.",
            "icon": "Trophy",
            "unlockedAt": str(datetime.utcnow())
        })
    
    profile = {
        "id": str(db_assess.id),
        "name": current_user.name,
        "email": current_user.email,
        "avatarInitials": "".join([n[0] for n in current_user.name.split() if n])[:2].upper() or "U",
        "targetRole": db_assess.career_goal,
        "targetRoleCategory": "Cybersecurity",
        "experience": "Beginner" if (db_assess.readiness_score or 0) < 50 else ("Intermediate" if (db_assess.readiness_score or 0) < 80 else "Advanced"),
        "readiness": db_assess.readiness_score,
        "weeklyStudyHours": db_assess.weekly_hours or 10,
        "learningPreferences": db_assess.learning_preferences or ["videos", "labs"],
        "knownSkills": known,
        "missingSkills": missing,
        "completedSkills": [],
        "projects": [],
        "certifications": [],
        "achievements": achievements,
        "totalStudyHours": 0,
        "currentStreak": current_streak,
        "longestStreak": current_streak,
        "joinedAt": str(current_user.created_at),
        "lastActive": str(datetime.utcnow()),
        "roadmapProgress": roadmap_progress
    }
    
    # Build Mentor Context
    today_mission = next((s for s in roadmap_steps if s.get("status") == "available" or s.get("status") == "in-progress"), None)
    next_milestone = next((s for s in roadmap_steps if s.get("type") == "milestone" and s.get("status") != "completed"), None)
    last_completed = next((s for s in reversed(roadmap_steps) if s.get("status") == "completed"), None)
    
    mentor_context = {
        "todayMission": today_mission,
        "nextMilestone": next_milestone,
        "lastCompleted": last_completed,
        "recentAchievement": None,
        "currentStreak": 1,
        "weeklyProgress": 0,
        "estimatedTimeToReady": f"{db_roadmap.estimated_weeks} weeks" if db_roadmap else "Unknown"
    }
    
    # Build Weekly Progress (Mocked for now since Progress model isn't populated)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly_progress = [{"day": d, "hours": 0, "goal": (db_assess.weekly_hours or 10) / 7} for d in days]
    weekly_progress[0]["hours"] = 2  # Fake some progress
    
    daily_mission = {
        "node": today_mission,
        "estimatedMinutes": today_mission.get("estimatedHours", 1) * 60 if today_mission else 60,
        "priority": "high"
    } if today_mission else None

    return {
        "success": True,
        "data": {
            "profile": profile,
            "roadmap": roadmap_steps,
            "mentorContext": mentor_context,
            "weeklyProgress": weekly_progress,
            "dailyMission": daily_mission
        }
    }


@router.get("/career/readiness")
async def get_career_readiness(current_user: User = Depends(get_current_user)):
    from repositories.repositories import AssessmentRepository
    from services.career_service import CareerService
    from app.domain.models import CyberProfile, Skill
    
    assessment_repo = AssessmentRepository()
    db_assess = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(db_assess, list):
        db_assess = db_assess[0] if db_assess else None
        
    if not db_assess:
        not_found("No assessment found")
        
    # Reconstruct profile
    matched = db_assess.matched_skills or []
    profile = CyberProfile(
        skills=[Skill(name=s, category="", difficulty="beginner") for s in matched],
    )
    
    svc = CareerService()
    assessment = svc.analyze(profile, str(db_assess.career_goal))
    
    return {
        "success": True,
        "data": {
            "readiness_score": assessment.readiness_score,
            "career_goal": assessment.target_career.title,
            "matched_skills": [s.name for s in assessment.matched_skills],
            "missing_skills": [s.name for s in assessment.missing_skills]
        }
    }


@router.get("/recommendations")
async def get_recommendations(current_user: User = Depends(get_current_user)):
    from repositories.repositories import AssessmentRepository
    from services.recommendation_service import RecommendationService
    from app.domain.models import CyberProfile, Skill
    
    assessment_repo = AssessmentRepository()
    db_assess = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(db_assess, list):
        db_assess = db_assess[0] if db_assess else None
        
    if not db_assess:
        not_found("No assessment found")
        
    matched = db_assess.matched_skills or []
    profile = CyberProfile(
        skills=[Skill(name=s, category="", difficulty="beginner") for s in matched]
    )
    
    svc = RecommendationService()
    rec = svc.get_next_recommendation(profile, str(db_assess.career_goal))
    
    return {
        "success": True,
        "data": {
            "next_skill": rec.next_skill,
            "next_project": rec.next_project,
            "reason": rec.reason,
            "estimated_hours": rec.estimated_hours,
            "difficulty": rec.difficulty
        }
    }


@router.post("/progress/update")
async def update_progress(request: dict, current_user: User = Depends(get_current_user)):
    skill_name = request.get("skill_name")
    project_title = request.get("project_title")
    study_hours = request.get("study_hours", 0)
    
    from repositories.repositories import AssessmentRepository, RoadmapRepository
    from services.progress_service import ProgressService
    from app.domain.models import CyberProfile, Skill
    
    assessment_repo = AssessmentRepository()
    db_assess = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(db_assess, list):
        db_assess = db_assess[0] if db_assess else None
        
    if not db_assess:
        not_found("No assessment found")
        
    matched = db_assess.matched_skills or []
    profile = CyberProfile(
        skills=[Skill(name=s, category="", difficulty="beginner") for s in matched]
    )
    
    svc = ProgressService()
    result = {}
    target = str(db_assess.career_goal)
    
    try:
        if skill_name:
            result = svc.complete_skill(profile, skill_name, target)
        elif project_title:
            result = svc.complete_project(profile, project_title, target)
        elif study_hours > 0:
            result = svc.add_study_hours(profile, study_hours, target)
        
        updated_profile = result.get("profile")
        if updated_profile:
            new_matched = [s.name for s in updated_profile.skills]
            db_assess.matched_skills = new_matched
            db_assess.readiness_score = result.get("readiness_score", db_assess.readiness_score)
            from database.session import SessionLocal
            db = SessionLocal()
            try:
                db.merge(db_assess)
                db.commit()
            finally:
                db.close()
    except Exception as e:
        logger.warning("Failed to update progress: %s", e)
        
    return {
        "success": True,
        "data": result
    }


@router.post("/skills/evidence/analyze")
async def analyze_skill_evidence(
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user),
):
    from repositories.repositories import SkillEvidenceRepository, UserSkillProfileRepository
    from services.skill_evidence_orchestrator import skill_evidence_orchestrator
    import datetime

    evidence_repo = SkillEvidenceRepository()
    profile_repo = UserSkillProfileRepository()

    existing_profile = profile_repo.get_by_user_id(str(current_user.id))
    if existing_profile and existing_profile.analysis_status == "completed" and not force_refresh:
        existing_evidence = evidence_repo.get_by_user_id(str(current_user.id))
        return {
            "success": True,
            "data": {
                "status": "completed",
                "total_skills": existing_profile.total_skills,
                "high_confidence": existing_profile.high_confidence_count,
                "medium_confidence": existing_profile.medium_confidence_count,
                "low_confidence": existing_profile.low_confidence_count,
                "minimal_confidence": existing_profile.minimal_confidence_count,
                "average_confidence": existing_profile.average_confidence,
                "analyzed_at": str(existing_profile.analyzed_at) if existing_profile.analyzed_at else None,
                "cached": True,
            },
        }

    if existing_profile:
        profile_id = str(existing_profile.id)
        profile_repo.update(profile_id, analysis_status="analyzing")
        evidence_repo.delete_by_user_id(str(current_user.id))
    else:
        new_profile = profile_repo.create(
            user_id=str(current_user.id),
            analysis_status="analyzing",
        )
        profile_id = str(new_profile.id)

    try:
        results = skill_evidence_orchestrator.analyze_user(str(current_user.id))

        evidence_items = []
        total_conf = 0.0
        high = 0
        medium = 0
        low = 0
        minimal = 0

        for skill_name, agg in results.items():
            evidence_items.append({
                "skill_name": agg.skill_name,
                "skill_id": agg.skill_id,
                "category": agg.category,
                "confidence": int(agg.confidence * 100),
                "confidence_level": agg.confidence_level,
                "sources": [
                    {
                        "source": s.get("source", ""),
                        "raw_confidence": s.get("raw_confidence", 0),
                        "effective_confidence": s.get("effective_confidence", 0),
                        "weight": s.get("weight", 0),
                        "contribution": s.get("contribution", 0),
                        "repository": s.get("repository"),
                        "evidence_text": s.get("evidence_text"),
                        "details": s.get("details", {}),
                    }
                    for s in (agg.sources if isinstance(agg.sources, list) else [])
                ],
                "evidence_count": agg.evidence_count,
                "strongest_source": agg.strongest_source,
                "last_updated": agg.last_updated,
            })
            total_conf += agg.confidence
            if agg.confidence_level == "high":
                high += 1
            elif agg.confidence_level == "medium":
                medium += 1
            elif agg.confidence_level == "low":
                low += 1
            else:
                minimal += 1

        if evidence_items:
            evidence_repo.upsert_many(str(current_user.id), evidence_items)

        avg_conf = int((total_conf / len(results) * 100)) if results else 0
        now = datetime.datetime.now(datetime.timezone.utc)

        profile_repo.update(
            profile_id,
            total_skills=len(results),
            high_confidence_count=high,
            medium_confidence_count=medium,
            low_confidence_count=low,
            minimal_confidence_count=minimal,
            average_confidence=avg_conf,
            analysis_status="completed",
            analyzed_at=now,
        )

        return {
            "success": True,
            "data": {
                "status": "completed",
                "total_skills": len(results),
                "high_confidence": high,
                "medium_confidence": medium,
                "low_confidence": low,
                "minimal_confidence": minimal,
                "average_confidence": avg_conf,
                "analyzed_at": str(now),
                "cached": False,
            },
        }

    except Exception as e:
        logger.error("Skill evidence analysis failed: %s", e)
        profile_repo.update(profile_id, analysis_status="failed", analysis_error=str(e))
        internal_error("Skill evidence analysis failed. Please try again later.")


@router.get("/skills/evidence")
async def get_skill_evidence(current_user: User = Depends(get_current_user)):
    from repositories.repositories import SkillEvidenceRepository, UserSkillProfileRepository

    evidence_repo = SkillEvidenceRepository()
    profile_repo = UserSkillProfileRepository()

    profile = profile_repo.get_by_user_id(str(current_user.id))
    if not profile or profile.analysis_status != "completed":
        return {
            "success": True,
            "data": {
                "evidence": [],
                "total_skills": 0,
                "analysis_status": profile.analysis_status if profile else "pending",
            },
        }

    evidence_items = evidence_repo.get_by_user_id(str(current_user.id))

    return {
        "success": True,
        "data": {
            "evidence": [
                {
                    "skill_id": e.skill_id,
                    "skill_name": e.skill_name,
                    "category": e.category,
                    "confidence": e.confidence,
                    "confidence_level": e.confidence_level,
                    "sources": e.sources or [],
                    "evidence_count": e.evidence_count,
                    "strongest_source": e.strongest_source,
                    "last_updated": e.last_updated,
                }
                for e in evidence_items
            ],
            "total_skills": profile.total_skills,
            "high_confidence": profile.high_confidence_count,
            "medium_confidence": profile.medium_confidence_count,
            "low_confidence": profile.low_confidence_count,
            "minimal_confidence": profile.minimal_confidence_count,
            "average_confidence": profile.average_confidence,
            "analysis_status": profile.analysis_status,
        },
    }


@router.get("/skills/evidence/{skill_id}")
async def get_skill_evidence_detail(
    skill_id: str,
    current_user: User = Depends(get_current_user),
):
    from repositories.repositories import SkillEvidenceRepository

    evidence_repo = SkillEvidenceRepository()
    evidence = evidence_repo.get_by_user_and_skill(str(current_user.id), skill_id)

    if not evidence:
        not_found("Skill evidence not found")

    return {
        "success": True,
        "data": {
            "skill_id": evidence.skill_id,
            "skill_name": evidence.skill_name,
            "category": evidence.category,
            "confidence": evidence.confidence,
            "confidence_level": evidence.confidence_level,
            "sources": evidence.sources or [],
            "evidence_count": evidence.evidence_count,
            "strongest_source": evidence.strongest_source,
            "last_updated": evidence.last_updated,
        },
    }


@router.get("/career/roles")
async def list_career_roles(
    current_user: User = Depends(get_current_user),
):
    from services.role_adapter import RoleAdapter

    adapter = RoleAdapter()
    roles = adapter.get_all_roles_enriched()

    items = []
    for role in roles:
        items.append({
            "role_id": role["role_id"],
            "role_name": role["role_name"],
            "description": role["description"],
            "required_skills_count": len(role["required_skills"]),
            "optional_skills_count": len(role["optional_skills"]),
            "recommended_certifications": role["recommended_certifications"],
            "estimated_duration": role.get("estimated_duration"),
        })

    return {
        "success": True,
        "data": {"roles": items, "total": len(items)},
    }


@router.get("/career/roles/{role_id}")
async def get_career_role_detail(
    role_id: str,
    current_user: User = Depends(get_current_user),
):
    from services.role_adapter import RoleAdapter

    adapter = RoleAdapter()
    role = adapter.get_role_enriched(role_id)

    if not role:
        not_found(f"Role '{role_id}' not found")

    return {
        "success": True,
        "data": role,
    }


@router.post("/career/role/select")
async def select_target_role(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    from services.role_adapter import RoleAdapter

    role_id = request.get("role_id")
    if not role_id:
        validation_error("role_id is required")

    adapter = RoleAdapter()
    role = adapter.get_role_enriched(role_id)

    if not role:
        not_found(f"Role '{role_id}' not found")

    return {
        "success": True,
        "data": {
            "role_id": role_id,
            "role_name": role["role_name"],
            "message": f"Target role set to {role['role_name']}",
        },
    }


@router.post("/career/gap-analysis")
async def run_gap_analysis(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    from services.role_gap_analysis_service import RoleGapAnalysisService
    from services.gap_analysis_service import GapAnalysisService
    from services.role_adapter import RoleAdapter
    from app.ai.orchestrator import AIOrchestrator
    from app.ai.gap_explanation import GapExplanationService

    role_id = request.get("role_id")
    force_refresh = request.get("force_refresh", False)

    if not role_id:
        validation_error("role_id is required")

    user_id = str(current_user.id)

    role_adapter = RoleAdapter()
    gap_service = GapAnalysisService(role_adapter=role_adapter)
    analysis_svc = RoleGapAnalysisService(
        gap_analysis_service=gap_service,
        role_adapter=role_adapter,
    )

    if not force_refresh:
        saved = analysis_svc.get_saved_analysis(user_id)
        if saved and saved.get("role_id") == role_id:
            return {
                "success": True,
                "data": saved,
                "cached": True,
            }

    result = analysis_svc.analyze_role_gap(user_id, role_id)

    if "error" in result:
        not_found(result["error"])

    try:
        orchestrator = AIOrchestrator(provider_name="gemini", fallback_provider_name="mistral")
        if orchestrator.is_configured():
            explainer = GapExplanationService(orchestrator=orchestrator)
            explanation = explainer.generate_explanation(
                role_name=result["role_name"],
                readiness_score=result["readiness_score"],
                skill_gaps=result["skill_gaps"],
                next_skill=result.get("recommended_next_skill"),
            )
            if explanation:
                result["ai_explanation"] = explanation.get("summary", "")
    except Exception as e:
        logger.warning("AI explanation generation failed: %s", e)

    analysis_svc.save_analysis(user_id, result)

    return {
        "success": True,
        "data": result,
        "cached": False,
    }


@router.get("/career/gap-analysis")
async def get_gap_analysis(
    current_user: User = Depends(get_current_user),
):
    from services.role_gap_analysis_service import RoleGapAnalysisService

    user_id = str(current_user.id)
    analysis_svc = RoleGapAnalysisService()

    saved = analysis_svc.get_saved_analysis(user_id)
    if not saved:
        return {
            "success": True,
            "data": None,
            "message": "No role analysis found. Select a target role first.",
        }

    return {
        "success": True,
        "data": saved,
    }


@router.get("/career/next-skill")
async def get_next_skill_recommendation(
    current_user: User = Depends(get_current_user),
):
    from services.role_gap_analysis_service import RoleGapAnalysisService

    user_id = str(current_user.id)
    analysis_svc = RoleGapAnalysisService()

    next_skill = analysis_svc.get_next_skill(user_id)
    if not next_skill:
        return {
            "success": True,
            "data": None,
            "message": "No recommendation available. Run a gap analysis first.",
        }

    return {
        "success": True,
        "data": next_skill,
    }
