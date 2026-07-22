from database.session import SessionLocal
from models.sqlalchemy_models import User, Assessment, Roadmap, ChatHistory, ResumeReview, ResumeProfile, GitHubProfile, GitHubRepositoryEvidence, SkillEvidence, UserSkillProfile, CareerRoleAnalysis, CareerEvidenceEvent, CareerChangeLog, RoadmapVersion


class UserRepository:
    def get_by_id(self, user_id: str):
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    def get_by_email(self, email: str):
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()


class AssessmentRepository:
    def get_by_id(self, assessment_id: str):
        db = SessionLocal()
        try:
            return db.query(Assessment).filter(Assessment.id == assessment_id).first()
        finally:
            db.close()

    def get_by_user_id(self, user_id: str, limit: int = 20):
        db = SessionLocal()
        try:
            return (
                db.query(Assessment)
                .filter(Assessment.user_id == user_id)
                .order_by(Assessment.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def create(self, user_id: str, career_goal: str, **kwargs) -> Assessment:
        db = SessionLocal()
        try:
            assessment = Assessment(user_id=user_id, career_goal=career_goal, **kwargs)
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            return assessment
        finally:
            db.close()


class RoadmapRepository:
    def get_by_assessment(self, assessment_id: str):
        db = SessionLocal()
        try:
            return db.query(Roadmap).filter(Roadmap.assessment_id == assessment_id).first()
        finally:
            db.close()

    def get_by_user_id(self, user_id: str, limit: int = 10):
        db = SessionLocal()
        try:
            return (
                db.query(Roadmap)
                .filter(Roadmap.user_id == user_id)
                .order_by(Roadmap.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def get_latest_by_user_and_assessment(self, user_id: str, assessment_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(Roadmap)
                .filter(Roadmap.user_id == user_id, Roadmap.assessment_id == assessment_id)
                .order_by(Roadmap.version.desc())
                .first()
            )
        finally:
            db.close()

    def create(self, assessment_id: str, steps: list, total_hours: int, estimated_weeks: int, **kwargs) -> Roadmap:
        db = SessionLocal()
        try:
            roadmap = Roadmap(
                assessment_id=assessment_id,
                steps=steps,
                total_hours=total_hours,
                estimated_weeks=estimated_weeks,
                **kwargs,
            )
            db.add(roadmap)
            db.commit()
            db.refresh(roadmap)
            return roadmap
        finally:
            db.close()

    def update_steps(self, roadmap_id: str, steps: list) -> Roadmap:
        db = SessionLocal()
        try:
            roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
            if roadmap:
                roadmap.steps = steps
                db.commit()
                db.refresh(roadmap)
            return roadmap
        finally:
            db.close()

    def update(self, roadmap_id: str, **kwargs) -> Roadmap:
        db = SessionLocal()
        try:
            roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
            if roadmap:
                for key, value in kwargs.items():
                    if hasattr(roadmap, key):
                        setattr(roadmap, key, value)
                db.commit()
                db.refresh(roadmap)
            return roadmap
        finally:
            db.close()


class ChatHistoryRepository:
    def get_by_user_id(self, user_id: str, limit: int = 50):
        db = SessionLocal()
        try:
            return (
                db.query(ChatHistory)
                .filter(ChatHistory.user_id == user_id)
                .order_by(ChatHistory.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def get_by_session(self, session_id: str, limit: int = 20):
        db = SessionLocal()
        try:
            return (
                db.query(ChatHistory)
                .filter(ChatHistory.session_id == session_id)
                .order_by(ChatHistory.created_at.asc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def create(self, user_id: str, session_id: str, question: str, answer: str) -> ChatHistory:
        db = SessionLocal()
        try:
            chat = ChatHistory(
                user_id=user_id,
                assessment_id="00000000-0000-0000-0000-000000000000",
                session_id=session_id,
                question=question,
                answer=answer,
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)
            return chat
        finally:
            db.close()


class ResumeReviewRepository:
    def get_by_user_id(self, user_id: str, limit: int = 20):
        db = SessionLocal()
        try:
            return (
                db.query(ResumeReview)
                .filter(ResumeReview.user_id == user_id)
                .order_by(ResumeReview.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def create(self, user_id: str, career_goal: str, feedback: str) -> ResumeReview:
        db = SessionLocal()
        try:
            review = ResumeReview(
                user_id=user_id,
                career_goal=career_goal,
                feedback=feedback,
            )
            db.add(review)
            db.commit()
            db.refresh(review)
            return review
        finally:
            db.close()


class ResumeProfileRepository:
    def get_by_id(self, profile_id: str):
        db = SessionLocal()
        try:
            return db.query(ResumeProfile).filter(ResumeProfile.id == profile_id).first()
        finally:
            db.close()

    def get_latest_by_user_id(self, user_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(ResumeProfile)
                .filter(ResumeProfile.user_id == user_id)
                .order_by(ResumeProfile.created_at.desc())
                .first()
            )
        finally:
            db.close()

    def get_by_user_id(self, user_id: str, limit: int = 20):
        db = SessionLocal()
        try:
            return (
                db.query(ResumeProfile)
                .filter(ResumeProfile.user_id == user_id)
                .order_by(ResumeProfile.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def create(self, user_id: str, original_filename: str, file_type: str, file_size: int = 0, raw_text: str = None) -> ResumeProfile:
        db = SessionLocal()
        try:
            profile = ResumeProfile(
                user_id=user_id,
                original_filename=original_filename,
                file_type=file_type,
                file_size=file_size,
                raw_text=raw_text,
                processing_status="uploaded",
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile
        finally:
            db.close()

    def update_status(self, profile_id: str, status: str, error: str = None):
        db = SessionLocal()
        try:
            profile = db.query(ResumeProfile).filter(ResumeProfile.id == profile_id).first()
            if profile:
                profile.processing_status = status
                if error:
                    profile.processing_error = error
                db.commit()
                db.refresh(profile)
            return profile
        finally:
            db.close()

    def update_result(self, profile_id: str, extracted_profile: dict, extracted_urls: dict, raw_text: str = None):
        db = SessionLocal()
        try:
            profile = db.query(ResumeProfile).filter(ResumeProfile.id == profile_id).first()
            if profile:
                profile.processing_status = "completed"
                profile.extracted_profile = extracted_profile
                profile.extracted_urls = extracted_urls
                if raw_text:
                    profile.raw_text = raw_text
                db.commit()
                db.refresh(profile)
            return profile
        finally:
            db.close()

    def delete(self, profile_id: str):
        db = SessionLocal()
        try:
            profile = db.query(ResumeProfile).filter(ResumeProfile.id == profile_id).first()
            if profile:
                db.delete(profile)
                db.commit()
        finally:
            db.close()


class GitHubProfileRepository:
    def get_by_id(self, profile_id: str):
        db = SessionLocal()
        try:
            return db.query(GitHubProfile).filter(GitHubProfile.id == profile_id).first()
        finally:
            db.close()

    def get_latest_by_user_id(self, user_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(GitHubProfile)
                .filter(GitHubProfile.user_id == user_id)
                .order_by(GitHubProfile.created_at.desc())
                .first()
            )
        finally:
            db.close()

    def create(self, user_id: str, username: str, profile_url: str, **kwargs) -> GitHubProfile:
        db = SessionLocal()
        try:
            profile = GitHubProfile(
                user_id=user_id,
                username=username,
                profile_url=profile_url,
                **kwargs,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile
        finally:
            db.close()

    def update_status(self, profile_id: str, status: str, error: str = None):
        db = SessionLocal()
        try:
            profile = db.query(GitHubProfile).filter(GitHubProfile.id == profile_id).first()
            if profile:
                profile.processing_status = status
                if error:
                    profile.processing_error = error
                db.commit()
                db.refresh(profile)
            return profile
        finally:
            db.close()

    def update_result(self, profile_id: str, **kwargs):
        db = SessionLocal()
        try:
            profile = db.query(GitHubProfile).filter(GitHubProfile.id == profile_id).first()
            if profile:
                for key, value in kwargs.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                db.commit()
                db.refresh(profile)
            return profile
        finally:
            db.close()

    def delete(self, profile_id: str):
        db = SessionLocal()
        try:
            profile = db.query(GitHubProfile).filter(GitHubProfile.id == profile_id).first()
            if profile:
                db.query(GitHubRepositoryEvidence).filter(
                    GitHubRepositoryEvidence.github_profile_id == profile_id
                ).delete()
                db.delete(profile)
                db.commit()
        finally:
            db.close()


class GitHubRepositoryEvidenceRepository:
    def get_by_profile_id(self, github_profile_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(GitHubRepositoryEvidence)
                .filter(GitHubRepositoryEvidence.github_profile_id == github_profile_id)
                .order_by(GitHubRepositoryEvidence.stars.desc())
                .all()
            )
        finally:
            db.close()

    def create(self, github_profile_id: str, **kwargs) -> GitHubRepositoryEvidence:
        db = SessionLocal()
        try:
            evidence = GitHubRepositoryEvidence(
                github_profile_id=github_profile_id,
                **kwargs,
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)
            return evidence
        finally:
            db.close()

    def create_many(self, github_profile_id: str, items: list) -> list:
        db = SessionLocal()
        try:
            created = []
            for item in items:
                evidence = GitHubRepositoryEvidence(
                    github_profile_id=github_profile_id,
                    **item,
                )
                db.add(evidence)
                created.append(evidence)
            db.commit()
            for e in created:
                db.refresh(e)
            return created
        finally:
            db.close()

    def delete_by_profile_id(self, github_profile_id: str):
        db = SessionLocal()
        try:
            db.query(GitHubRepositoryEvidence).filter(
                GitHubRepositoryEvidence.github_profile_id == github_profile_id
            ).delete()
            db.commit()
        finally:
            db.close()


class SkillEvidenceRepository:
    def get_by_user_id(self, user_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(SkillEvidence)
                .filter(SkillEvidence.user_id == user_id)
                .order_by(SkillEvidence.confidence.desc())
                .all()
            )
        finally:
            db.close()

    def get_by_user_and_skill(self, user_id: str, skill_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(SkillEvidence)
                .filter(
                    SkillEvidence.user_id == user_id,
                    SkillEvidence.skill_id == skill_id,
                )
                .first()
            )
        finally:
            db.close()

    def upsert_many(self, user_id: str, items: list) -> list:
        db = SessionLocal()
        try:
            created = []
            for item in items:
                existing = (
                    db.query(SkillEvidence)
                    .filter(
                        SkillEvidence.user_id == user_id,
                        SkillEvidence.skill_id == item.get("skill_id"),
                    )
                    .first()
                )
                if existing:
                    existing.skill_name = item.get("skill_name", existing.skill_name)
                    existing.category = item.get("category", existing.category)
                    existing.confidence = item.get("confidence", existing.confidence)
                    existing.confidence_level = item.get("confidence_level", existing.confidence_level)
                    existing.sources = item.get("sources", existing.sources)
                    existing.evidence_count = item.get("evidence_count", existing.evidence_count)
                    existing.strongest_source = item.get("strongest_source", existing.strongest_source)
                    existing.last_updated = item.get("last_updated", existing.last_updated)
                    db.refresh(existing)
                    created.append(existing)
                else:
                    evidence = SkillEvidence(
                        user_id=user_id,
                        **item,
                    )
                    db.add(evidence)
                    created.append(evidence)
            db.commit()
            for e in created:
                db.refresh(e)
            return created
        finally:
            db.close()

    def delete_by_user_id(self, user_id: str):
        db = SessionLocal()
        try:
            db.query(SkillEvidence).filter(SkillEvidence.user_id == user_id).delete()
            db.commit()
        finally:
            db.close()


class UserSkillProfileRepository:
    def get_by_user_id(self, user_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(UserSkillProfile)
                .filter(UserSkillProfile.user_id == user_id)
                .order_by(UserSkillProfile.created_at.desc())
                .first()
            )
        finally:
            db.close()

    def create(self, user_id: str, **kwargs) -> UserSkillProfile:
        db = SessionLocal()
        try:
            profile = UserSkillProfile(user_id=user_id, **kwargs)
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile
        finally:
            db.close()

    def update(self, profile_id: str, **kwargs):
        db = SessionLocal()
        try:
            profile = db.query(UserSkillProfile).filter(UserSkillProfile.id == profile_id).first()
            if profile:
                for key, value in kwargs.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                db.commit()
                db.refresh(profile)
            return profile
        finally:
            db.close()


class CareerRoleAnalysisRepository:
    def get_by_user_id(self, user_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(CareerRoleAnalysis)
                .filter(CareerRoleAnalysis.user_id == user_id)
                .order_by(CareerRoleAnalysis.created_at.desc())
                .first()
            )
        finally:
            db.close()

    def get_by_user_and_role(self, user_id: str, role_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(CareerRoleAnalysis)
                .filter(
                    CareerRoleAnalysis.user_id == user_id,
                    CareerRoleAnalysis.role_id == role_id,
                )
                .first()
            )
        finally:
            db.close()

    def create(self, user_id: str, **kwargs) -> CareerRoleAnalysis:
        db = SessionLocal()
        try:
            analysis = CareerRoleAnalysis(user_id=user_id, **kwargs)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis
        finally:
            db.close()

    def update(self, analysis_id: str, **kwargs):
        db = SessionLocal()
        try:
            analysis = db.query(CareerRoleAnalysis).filter(CareerRoleAnalysis.id == analysis_id).first()
            if analysis:
                for key, value in kwargs.items():
                    if hasattr(analysis, key):
                        setattr(analysis, key, value)
                db.commit()
                db.refresh(analysis)
            return analysis
        finally:
            db.close()

    def delete_by_user_id(self, user_id: str):
        db = SessionLocal()
        try:
            db.query(CareerRoleAnalysis).filter(CareerRoleAnalysis.user_id == user_id).delete()
            db.commit()
        finally:
            db.close()


class CareerEvidenceEventRepository:
    def get_by_id(self, event_id: str):
        db = SessionLocal()
        try:
            return db.query(CareerEvidenceEvent).filter(CareerEvidenceEvent.id == event_id).first()
        finally:
            db.close()

    def get_by_user_id(self, user_id: str, limit: int = 50):
        db = SessionLocal()
        try:
            return (
                db.query(CareerEvidenceEvent)
                .filter(CareerEvidenceEvent.user_id == user_id)
                .order_by(CareerEvidenceEvent.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def get_pending_events(self, user_id: str = None, limit: int = 100):
        db = SessionLocal()
        try:
            q = db.query(CareerEvidenceEvent).filter(CareerEvidenceEvent.status == "pending")
            if user_id:
                q = q.filter(CareerEvidenceEvent.user_id == user_id)
            return q.order_by(CareerEvidenceEvent.created_at.asc()).limit(limit).all()
        finally:
            db.close()

    def get_by_idempotency_key(self, key: str):
        db = SessionLocal()
        try:
            return db.query(CareerEvidenceEvent).filter(CareerEvidenceEvent.idempotency_key == key).first()
        finally:
            db.close()

    def create(self, user_id: str, event_type: str, event_data: dict = None, idempotency_key: str = None) -> CareerEvidenceEvent:
        db = SessionLocal()
        try:
            event = CareerEvidenceEvent(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data or {},
                idempotency_key=idempotency_key,
                status="pending",
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        finally:
            db.close()

    def update_status(self, event_id: str, status: str, error_message: str = None):
        db = SessionLocal()
        try:
            event = db.query(CareerEvidenceEvent).filter(CareerEvidenceEvent.id == event_id).first()
            if event:
                event.status = status
                if error_message:
                    event.error_message = error_message
                if status == "processed":
                    from datetime import datetime
                    event.processed_at = datetime.utcnow()
                if status == "failed":
                    event.retry_count = (event.retry_count or 0) + 1
                db.commit()
                db.refresh(event)
            return event
        finally:
            db.close()


class CareerChangeLogRepository:
    def get_by_user_id(self, user_id: str, limit: int = 100):
        db = SessionLocal()
        try:
            return (
                db.query(CareerChangeLog)
                .filter(CareerChangeLog.user_id == user_id)
                .order_by(CareerChangeLog.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def get_by_event_id(self, event_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(CareerChangeLog)
                .filter(CareerChangeLog.event_id == event_id)
                .order_by(CareerChangeLog.created_at.asc())
                .all()
            )
        finally:
            db.close()

    def create(self, user_id: str, event_id: str, change_type: str, **kwargs) -> CareerChangeLog:
        db = SessionLocal()
        try:
            log = CareerChangeLog(
                user_id=user_id,
                event_id=event_id,
                change_type=change_type,
                **kwargs,
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return log
        finally:
            db.close()


class RoadmapVersionRepository:
    def get_by_user_id(self, user_id: str, limit: int = 10):
        db = SessionLocal()
        try:
            return (
                db.query(RoadmapVersion)
                .filter(RoadmapVersion.user_id == user_id)
                .order_by(RoadmapVersion.version_number.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def get_latest_by_user(self, user_id: str):
        db = SessionLocal()
        try:
            return (
                db.query(RoadmapVersion)
                .filter(RoadmapVersion.user_id == user_id)
                .order_by(RoadmapVersion.version_number.desc())
                .first()
            )
        finally:
            db.close()

    def get_by_id(self, version_id: str):
        db = SessionLocal()
        try:
            return db.query(RoadmapVersion).filter(RoadmapVersion.id == version_id).first()
        finally:
            db.close()

    def create(self, user_id: str, assessment_id: str, version_number: int, **kwargs) -> RoadmapVersion:
        db = SessionLocal()
        try:
            version = RoadmapVersion(
                user_id=user_id,
                assessment_id=assessment_id,
                version_number=version_number,
                **kwargs,
            )
            db.add(version)
            db.commit()
            db.refresh(version)
            return version
        finally:
            db.close()

    def get_next_version_number(self, user_id: str) -> int:
        db = SessionLocal()
        try:
            latest = (
                db.query(RoadmapVersion)
                .filter(RoadmapVersion.user_id == user_id)
                .order_by(RoadmapVersion.version_number.desc())
                .first()
            )
            return (latest.version_number + 1) if latest else 1
        finally:
            db.close()
