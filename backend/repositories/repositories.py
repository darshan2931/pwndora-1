from database.session import SessionLocal
from models.sqlalchemy_models import User, Assessment, Roadmap


class UserRepository:
    def get_by_id(self, user_id: str):
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    def create(self, name: str, email: str) -> User:
        db = SessionLocal()
        try:
            user = User(name=name, email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()


class AssessmentRepository:
    def get_by_id(self, assessment_id: str):
        db = SessionLocal()
        try:
            return db.query(Assessment).filter(Assessment.id == assessment_id).first()
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
