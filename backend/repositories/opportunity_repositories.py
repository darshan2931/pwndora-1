import logging
from typing import Optional, List, Dict

from database.session import SessionLocal
from models.sqlalchemy_models import (
    CareerOpportunity, OpportunityRequirement, OpportunityMatch,
    SkillEvidence, Assessment,
)

logger = logging.getLogger(__name__)


class CareerOpportunityRepository:
    def get_all_active(self) -> List[CareerOpportunity]:
        db = SessionLocal()
        try:
            return db.query(CareerOpportunity).filter(CareerOpportunity.is_active == 1).all()
        finally:
            db.close()

    def get_by_id(self, opportunity_id: str) -> Optional[CareerOpportunity]:
        db = SessionLocal()
        try:
            return db.query(CareerOpportunity).filter(CareerOpportunity.id == opportunity_id).first()
        finally:
            db.close()

    def create(self, **kwargs) -> CareerOpportunity:
        db = SessionLocal()
        try:
            opp = CareerOpportunity(**kwargs)
            db.add(opp)
            db.commit()
            db.refresh(opp)
            return opp
        finally:
            db.close()

    def seed_opportunities(self, opportunities: List[dict]) -> int:
        db = SessionLocal()
        try:
            existing = db.query(CareerOpportunity).count()
            if existing > 0:
                return 0
            count = 0
            for opp_data in opportunities:
                requirements = opp_data.pop("requirements", [])
                opp = CareerOpportunity(**opp_data)
                db.add(opp)
                db.flush()
                for req in requirements:
                    req["opportunity_id"] = str(opp.id)
                    db.add(OpportunityRequirement(**req))
                count += 1
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            logger.error("Failed to seed opportunities: %s", e)
            return 0
        finally:
            db.close()


class OpportunityRequirementRepository:
    def get_by_opportunity_id(self, opportunity_id: str) -> List[OpportunityRequirement]:
        db = SessionLocal()
        try:
            return (
                db.query(OpportunityRequirement)
                .filter(OpportunityRequirement.opportunity_id == opportunity_id)
                .all()
            )
        finally:
            db.close()

    def get_required_skills(self, opportunity_id: str) -> List[OpportunityRequirement]:
        db = SessionLocal()
        try:
            return (
                db.query(OpportunityRequirement)
                .filter(
                    OpportunityRequirement.opportunity_id == opportunity_id,
                    OpportunityRequirement.requirement_type == "required",
                )
                .all()
            )
        finally:
            db.close()

    def get_preferred_skills(self, opportunity_id: str) -> List[OpportunityRequirement]:
        db = SessionLocal()
        try:
            return (
                db.query(OpportunityRequirement)
                .filter(
                    OpportunityRequirement.opportunity_id == opportunity_id,
                    OpportunityRequirement.requirement_type == "preferred",
                )
                .all()
            )
        finally:
            db.close()

    def get_certifications(self, opportunity_id: str) -> List[OpportunityRequirement]:
        db = SessionLocal()
        try:
            return (
                db.query(OpportunityRequirement)
                .filter(
                    OpportunityRequirement.opportunity_id == opportunity_id,
                    OpportunityRequirement.requirement_type == "certification",
                )
                .all()
            )
        finally:
            db.close()

    def create(self, **kwargs) -> OpportunityRequirement:
        db = SessionLocal()
        try:
            req = OpportunityRequirement(**kwargs)
            db.add(req)
            db.commit()
            db.refresh(req)
            return req
        finally:
            db.close()


class OpportunityMatchRepository:
    def get_by_user_id(self, user_id: str) -> List[OpportunityMatch]:
        db = SessionLocal()
        try:
            return (
                db.query(OpportunityMatch)
                .filter(OpportunityMatch.user_id == user_id)
                .order_by(OpportunityMatch.match_score.desc())
                .all()
            )
        finally:
            db.close()

    def get_by_user_and_opportunity(self, user_id: str, opportunity_id: str) -> Optional[OpportunityMatch]:
        db = SessionLocal()
        try:
            return (
                db.query(OpportunityMatch)
                .filter(
                    OpportunityMatch.user_id == user_id,
                    OpportunityMatch.opportunity_id == opportunity_id,
                )
                .first()
            )
        finally:
            db.close()

    def upsert(self, user_id: str, opportunity_id: str, **kwargs) -> OpportunityMatch:
        db = SessionLocal()
        try:
            existing = (
                db.query(OpportunityMatch)
                .filter(
                    OpportunityMatch.user_id == user_id,
                    OpportunityMatch.opportunity_id == opportunity_id,
                )
                .first()
            )
            if existing:
                for k, v in kwargs.items():
                    setattr(existing, k, v)
                db.commit()
                db.refresh(existing)
                return existing
            match = OpportunityMatch(user_id=user_id, opportunity_id=opportunity_id, **kwargs)
            db.add(match)
            db.commit()
            db.refresh(match)
            return match
        finally:
            db.close()

    def delete_by_user_id(self, user_id: str) -> None:
        db = SessionLocal()
        try:
            db.query(OpportunityMatch).filter(OpportunityMatch.user_id == user_id).delete()
            db.commit()
        finally:
            db.close()
