from database.session import SessionLocal
from models.sqlalchemy_models import User, Assessment, Roadmap, ChatHistory, ResumeReview


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

    def create(self, assessment_id: str, steps: list, total_hours: int, estimated_weeks: int) -> Roadmap:
        db = SessionLocal()
        try:
            roadmap = Roadmap(
                assessment_id=assessment_id,
                steps=steps,
                total_hours=total_hours,
                estimated_weeks=estimated_weeks,
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
                # SQLAlchemy JSON columns need explicit flag modification sometimes
                # or just re-assigning the new dict/list copy
                roadmap.steps = steps
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
