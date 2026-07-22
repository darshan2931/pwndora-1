import os
import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime


# ─── Impact Analysis Tests ─────────────────────────────────────────────────────

class TestImpactAnalysis:

    def test_impact_analysis_initialization(self):
        from services.impact_analysis import ImpactAnalysis
        ia = ImpactAnalysis()
        assert ia is not None

    def test_evidence_strength_for_event_types(self):
        from services.impact_analysis import ImpactAnalysis
        ia = ImpactAnalysis()

        skill_event = ia.get_evidence_strength_for_event("roadmap_skill_completed")
        assert skill_event["base_strength"] == 0.20
        assert skill_event["evidence_type"] == "learning_completion"

        project_event = ia.get_evidence_strength_for_event("roadmap_project_completed")
        assert project_event["base_strength"] == 0.75
        assert project_event["evidence_type"] == "project_completion"

        cert_event = ia.get_evidence_strength_for_event("roadmap_certification_completed")
        assert cert_event["base_strength"] == 0.80
        assert cert_event["evidence_type"] == "certification_completion"

        github_event = ia.get_evidence_strength_for_event("github_repository_linked")
        assert github_event["base_strength"] == 0.60

        assessment_event = ia.get_evidence_strength_for_event("assessment_completed")
        assert assessment_event["base_strength"] == 0.50

        unknown_event = ia.get_evidence_strength_for_event("unknown_event")
        assert unknown_event["base_strength"] == 0.30

    def test_get_impacted_roles(self):
        from services.impact_analysis import ImpactAnalysis
        ia = ImpactAnalysis()
        impacted = ia.get_impacted_roles("SIEM")
        assert "SOC Analyst" in impacted

    def test_get_impacted_roles_empty_for_unknown_skill(self):
        from services.impact_analysis import ImpactAnalysis
        ia = ImpactAnalysis()
        impacted = ia.get_impacted_roles("CompletelyUnknownSkill123")
        assert impacted == []


# ─── Evidence Event Processor Tests ────────────────────────────────────────────

class TestEvidenceEventProcessor:

    def test_processor_initialization(self):
        from services.evidence_event_processor import EvidenceEventProcessor
        proc = EvidenceEventProcessor()
        assert proc is not None

    def test_confidence_level_classification(self):
        from services.evidence_event_processor import EvidenceEventProcessor
        proc = EvidenceEventProcessor()
        assert proc._confidence_level(85) == "high"
        assert proc._confidence_level(70) == "medium"
        assert proc._confidence_level(45) == "low"
        assert proc._confidence_level(20) == "minimal"
        assert proc._confidence_level(80) == "high"
        assert proc._confidence_level(60) == "medium"
        assert proc._confidence_level(40) == "low"

    @patch('services.evidence_event_processor.CareerEvidenceEventRepository')
    def test_create_event_idempotency_duplicate(self, mock_repo_cls):
        from services.evidence_event_processor import EvidenceEventProcessor

        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo

        existing_event = MagicMock()
        existing_event.id = "existing-id"
        existing_event.status = "processed"
        mock_repo.get_by_idempotency_key.return_value = existing_event

        proc = EvidenceEventProcessor(event_repo=mock_repo)
        result = proc.create_event(
            user_id="user-1",
            event_type="roadmap_skill_completed",
            event_data={"skill_id": "Linux"},
            idempotency_key="unique-key-1",
        )

        assert result["duplicate"] is True
        assert result["event_id"] == "existing-id"

    @patch('services.evidence_event_processor.CareerEvidenceEventRepository')
    def test_create_event_new(self, mock_repo_cls):
        from services.evidence_event_processor import EvidenceEventProcessor

        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.get_by_idempotency_key.return_value = None

        new_event = MagicMock()
        new_event.id = "new-event-id"
        new_event.status = "pending"
        mock_repo.create.return_value = new_event

        proc = EvidenceEventProcessor(event_repo=mock_repo)
        result = proc.create_event(
            user_id="user-1",
            event_type="roadmap_skill_completed",
            event_data={"skill_id": "Linux"},
            idempotency_key="unique-key-1",
        )

        assert result["duplicate"] is False
        assert result["event_id"] == "new-event-id"
        mock_repo.create.assert_called_once()


# ─── Adaptive Roadmap Service Tests ────────────────────────────────────────────

class TestAdaptiveRoadmapService:

    def test_adaptive_roadmap_initialization(self):
        from services.adaptive_roadmap import AdaptiveRoadmapService
        svc = AdaptiveRoadmapService()
        assert svc is not None

    @patch('services.adaptive_roadmap.RoadmapRepository')
    def test_should_regenerate_no_roadmap(self, mock_roadmap_repo_cls):
        from services.adaptive_roadmap import AdaptiveRoadmapService

        mock_repo = MagicMock()
        mock_roadmap_repo_cls.return_value = mock_repo
        mock_repo.get_latest_by_user_and_assessment.return_value = None
        mock_repo.get_by_user_id.return_value = []

        svc = AdaptiveRoadmapService(roadmap_repo=mock_repo)
        result = svc.should_regenerate(
            user_id="user-1",
            event_type="roadmap_skill_completed",
            confidence_delta=15,
            impacted_skills=["Linux"],
        )

        assert result["should_regenerate"] is False
        assert result["reason"] == "no_roadmap"

    @patch('services.adaptive_roadmap.RoadmapRepository')
    def test_should_regenerate_significant_change(self, mock_roadmap_repo_cls):
        from services.adaptive_roadmap import AdaptiveRoadmapService

        mock_repo = MagicMock()
        mock_roadmap_repo_cls.return_value = mock_repo

        mock_roadmap = MagicMock()
        mock_roadmap.id = "roadmap-1"
        mock_repo.get_latest_by_user_and_assessment.return_value = mock_roadmap

        svc = AdaptiveRoadmapService(roadmap_repo=mock_repo)
        result = svc.should_regenerate(
            user_id="user-1",
            event_type="roadmap_skill_completed",
            confidence_delta=15,
            impacted_skills=["Linux", "Networking"],
        )

        assert result["should_regenerate"] is True
        assert result["reason"] == "skill_milestone"

    @patch('services.adaptive_roadmap.RoadmapRepository')
    def test_should_regenerate_minor_change(self, mock_roadmap_repo_cls):
        from services.adaptive_roadmap import AdaptiveRoadmapService

        mock_repo = MagicMock()
        mock_roadmap_repo_cls.return_value = mock_repo

        mock_roadmap = MagicMock()
        mock_roadmap.id = "roadmap-1"
        mock_repo.get_latest_by_user_and_assessment.return_value = mock_roadmap

        svc = AdaptiveRoadmapService(roadmap_repo=mock_repo)
        result = svc.should_regenerate(
            user_id="user-1",
            event_type="roadmap_skill_completed",
            confidence_delta=3,
            impacted_skills=["Linux"],
        )

        assert result["should_regenerate"] is False
        assert result["reason"] == "minor_update"


# ─── Career Progress Service Tests ─────────────────────────────────────────────

class TestCareerProgressService:

    def test_career_progress_service_initialization(self):
        from services.career_progress_service import CareerProgressService
        svc = CareerProgressService()
        assert svc is not None


# ─── Progress Explanation Service Tests ─────────────────────────────────────────

class TestProgressExplanationService:

    def test_explanation_service_initialization(self):
        from app.ai.progress_explanation import ProgressExplanationService
        svc = ProgressExplanationService()
        assert svc is not None

    def test_fallback_explanation_positive_delta(self):
        from app.ai.progress_explanation import ProgressExplanationService
        svc = ProgressExplanationService()
        result = svc._fallback_explanation(
            change_type="roadmap_skill_completed",
            skill_name="Linux",
            old_confidence=30,
            new_confidence=50,
            old_readiness=25,
            new_readiness=28,
        )

        assert "summary" in result
        assert "skill_impact" in result
        assert "readiness_impact" in result
        assert "next_steps" in result
        assert "encouragement" in result
        assert "Linux" in result["summary"]
        assert "20%" in result["summary"] or "increased" in result["summary"]

    def test_fallback_explanation_no_delta(self):
        from app.ai.progress_explanation import ProgressExplanationService
        svc = ProgressExplanationService()
        result = svc._fallback_explanation(
            change_type="roadmap_skill_completed",
            skill_name="Linux",
            old_confidence=50,
            new_confidence=50,
            old_readiness=30,
            new_readiness=30,
        )

        assert "no confidence change" in result["summary"].lower() or "remains" in result["summary"].lower()

    def test_fallback_readiness_explanation(self):
        from app.ai.progress_explanation import ProgressExplanationService
        svc = ProgressExplanationService()
        result = svc._fallback_readiness_explanation(
            old_readiness=25,
            new_readiness=30,
            changes=[{"skill_name": "Linux", "old_confidence": 30, "new_confidence": 50}],
        )

        assert "summary" in result
        assert "5%" in result["summary"] or "improved" in result["summary"].lower()

    def test_parse_json_valid(self):
        from app.ai.progress_explanation import ProgressExplanationService
        svc = ProgressExplanationService()
        result = svc._parse_json('{"summary": "test", "key": "value"}')
        assert result == {"summary": "test", "key": "value"}

    def test_parse_json_with_code_blocks(self):
        from app.ai.progress_explanation import ProgressExplanationService
        svc = ProgressExplanationService()
        result = svc._parse_json('```json\n{"summary": "test"}\n```')
        assert result == {"summary": "test"}

    def test_parse_json_invalid(self):
        from app.ai.progress_explanation import ProgressExplanationService
        svc = ProgressExplanationService()
        result = svc._parse_json("not json at all")
        assert result is None


# ─── Career Change Log Repository Tests ────────────────────────────────────────

class TestCareerChangeLogRepository:

    def test_repository_importable(self):
        from repositories.repositories import CareerChangeLogRepository
        repo = CareerChangeLogRepository()
        assert repo is not None


# ─── Career Evidence Event Repository Tests ────────────────────────────────────

class TestCareerEvidenceEventRepository:

    def test_repository_importable(self):
        from repositories.repositories import CareerEvidenceEventRepository
        repo = CareerEvidenceEventRepository()
        assert repo is not None


# ─── Roadmap Version Repository Tests ──────────────────────────────────────────

class TestRoadmapVersionRepository:

    def test_repository_importable(self):
        from repositories.repositories import RoadmapVersionRepository
        repo = RoadmapVersionRepository()
        assert repo is not None


# ─── Model Tests ───────────────────────────────────────────────────────────────

class TestPhase6Models:

    def test_career_evidence_event_model_exists(self):
        from models.sqlalchemy_models import CareerEvidenceEvent
        assert CareerEvidenceEvent.__tablename__ == "career_evidence_events"

    def test_career_change_log_model_exists(self):
        from models.sqlalchemy_models import CareerChangeLog
        assert CareerChangeLog.__tablename__ == "career_change_logs"

    def test_roadmap_version_model_exists(self):
        from models.sqlalchemy_models import RoadmapVersion
        assert RoadmapVersion.__tablename__ == "roadmap_versions"
