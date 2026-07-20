import os
import logging
import datetime

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Depends
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy import select

from utils.validators import sanitize_string, sanitize_filename, validate_skills_list, validate_career_goal, validate_study_hours
from app.api.deps import get_current_user
from models.sqlalchemy_models import User, ChatMemory
from database.session import get_db, SessionLocal
from app.api.auth import router as auth_router

logger = logging.getLogger(__name__)
router = APIRouter()
router.include_router(auth_router)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _normalize_roadmap_steps(steps: list) -> list:
    """Convert old-format roadmap steps to the RoadmapNode format expected by the frontend."""
    normalized = []
    total = len(steps)
    for i, step in enumerate(steps):
        if "title" in step and "status" in step and "type" in step:
            step["completedAt"] = step.get("completedAt", step.get("completed_at"))
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
                resources.append({
                    "id": f"res-{i}-{j}",
                    "title": r,
                    "type": "article",
                    "url": "#",
                    "free": True,
                })
            elif isinstance(r, dict):
                resources.append(r)

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
        raise HTTPException(status_code=400, detail="Invalid assessment ID")

    try:
        from repositories.repositories import AssessmentRepository, RoadmapRepository  # pyrefly: ignore [missing-import]
        from knowledge.loader import knowledge_loader  # pyrefly: ignore [missing-import]
        assessment_repo = AssessmentRepository()
        roadmap_repo = RoadmapRepository()

        db_assess = assessment_repo.get_by_id(assessment_id)
        if not db_assess:
            raise HTTPException(status_code=404, detail="Assessment not found")
            
        if str(db_assess.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to view this assessment")

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


@router.post("/career/analyze")
async def analyze_career(
    career_goal: str = Form(...),
    study_hours: int = Form(10),
    manual_skills: str = Form(None),
    resume: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
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
            raise HTTPException(status_code=500, detail="Failed to parse resume")
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
        raise HTTPException(status_code=400, detail="No valid skills found in input")

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
        raise HTTPException(status_code=400, detail="career_goal is required")

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
        raise HTTPException(status_code=503, detail="Database is unavailable. Please try again later.")
    except Exception as e:
        logger.warning("Failed to save assessment to DB: %s", e)
        raise HTTPException(status_code=500, detail="Failed to save assessment")





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
            db_assess = db_assess[-1] if db_assess else None
            
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
        raise HTTPException(status_code=400, detail="Question is required")

    ai_svc = None
    try:
        ai_svc = _get_ai_service()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="AI Mentor service is not configured.")

    from repositories.repositories import AssessmentRepository, RoadmapRepository
    from app.ai.context_builder import ContextBuilder
    
    assessment_repo = AssessmentRepository()
    roadmap_repo = RoadmapRepository()
    
    db_assess = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(db_assess, list):
        db_assess = db_assess[-1] if db_assess else None
        
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
        raise HTTPException(status_code=503, detail="AI Mentor service is currently unavailable.")

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
        raise HTTPException(status_code=400, detail="Invalid skill name")
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
        raise HTTPException(status_code=400, detail="Career goal is required")
        
    ext = os.path.splitext(resume.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Use PDF, DOCX, or TXT.")

    if resume.size and resume.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")

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
        raise HTTPException(status_code=500, detail="Failed to process resume review")
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
            raise HTTPException(status_code=404, detail="Roadmap not found")

    assessment_repo = AssessmentRepository()
    user_assessments = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(user_assessments, list):
        user_assessment_ids = {str(a.id) for a in user_assessments}
    else:
        user_assessment_ids = {str(user_assessments.id)} if user_assessments else set()
    
    if str(roadmap.assessment_id) not in user_assessment_ids and str(roadmap.id) not in user_assessment_ids:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this roadmap")

    steps = _normalize_roadmap_steps(list(roadmap.steps))
    
    if step_index < 0 or step_index >= len(steps):
        raise HTTPException(status_code=400, detail="Invalid step index")
        
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
        db_assess = db_assess[-1] if db_assess else None
        
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
        db_assess = db_assess[-1] if db_assess else None
        
    if not db_assess:
        raise HTTPException(status_code=404, detail="No assessment found")
        
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
        db_assess = db_assess[-1] if db_assess else None
        
    if not db_assess:
        raise HTTPException(status_code=404, detail="No assessment found")
        
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
        db_assess = db_assess[-1] if db_assess else None
        
    if not db_assess:
        raise HTTPException(status_code=404, detail="No assessment found")
        
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
