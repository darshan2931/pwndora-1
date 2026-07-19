import sys
import re

with open("backend/app/api/routes.py", "r") as f:
    content = f.read()

# Replace /career/explain with /career/analyze and /career/save
old_explain = re.search(r'@router\.post\("/career/explain"\).*?return \{"success": True, "data": \{"explanation": text, "confidence": confidence\}\}', content, re.DOTALL)

with open("old_routes.py", "r") as f:
    old_content = f.read()
    
analyze_match = re.search(r'@router\.post\("/career/analyze"\).*?return \{"success": True, "data": result\}', old_content, re.DOTALL)
save_match = re.search(r'@router\.post\("/career/save"\).*?raise HTTPException\(status_code=500, detail="Failed to save assessment"\)', old_content, re.DOTALL)

new_career_endpoints = analyze_match.group(0) + "\n\n\n" + save_match.group(0)

content = content[:old_explain.start()] + new_career_endpoints + "\n\n\n" + content[old_explain.end():]

# Update /mentor/chat
mentor_chat_match = re.search(r'@router\.post\("/mentor/chat"\).*?return \{"success": True, "response": response\}', content, re.DOTALL)

new_mentor_chat = """@router.get("/mentor/greeting")
async def get_mentor_greeting(current_user: User = Depends(get_current_user)):
    from repositories.repositories import AssessmentRepository, RoadmapRepository
    from ai.context_builder import ContextBuilder
    
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
    from ai.context_builder import ContextBuilder
    
    assessment_repo = AssessmentRepository()
    roadmap_repo = RoadmapRepository()
    
    db_assess = assessment_repo.get_by_user_id(str(current_user.id))
    if isinstance(db_assess, list):
        db_assess = db_assess[-1] if db_assess else None
        
    context_str = ""
    if db_assess:
        db_roadmap = roadmap_repo.get_by_assessment(str(db_assess.id))
        context_str = ContextBuilder.build_mentor_context(current_user, db_assess, db_roadmap)

    db_histories = db.scalars(
        select(ChatHistory)
        .filter_by(user_id=str(current_user.id), session_id=session_id)
        .order_by(ChatHistory.created_at.asc())
    ).all()
    
    history = []
    for h in db_histories:
        history.append({"role": "user", "content": h.question})
        history.append({"role": "assistant", "content": h.answer})

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

    new_chat = ChatHistory(
        user_id=str(current_user.id),
        assessment_id=str(db_assess.id) if db_assess else "00000000-0000-0000-0000-000000000000",
        session_id=session_id,
        question=question,
        answer=response
    )
    db.add(new_chat)
    db.commit()

    return {"success": True, "response": response}"""

content = content[:mentor_chat_match.start()] + new_mentor_chat + content[mentor_chat_match.end():]

with open("backend/app/api/routes.py", "w") as f:
    f.write(content)
print("routes.py updated")
