import os
import json
import pytest
from unittest.mock import patch, MagicMock


# ─── Evidence Config Tests ───────────────────────────────────────────────────

class TestEvidenceConfig:

    def test_source_weight_returns_value(self):
        from services.evidence_config import EvidenceSource, get_source_weight
        assert get_source_weight(EvidenceSource.RESUME_CLAIM) > 0
        assert get_source_weight(EvidenceSource.CERTIFICATION_EARNED) > 0

    def test_source_max_confidence_returns_value(self):
        from services.evidence_config import EvidenceSource, get_source_max_confidence
        assert 0 < get_source_max_confidence(EvidenceSource.RESUME_CLAIM) <= 1.0
        assert 0 < get_source_max_confidence(EvidenceSource.CERTIFICATION_EARNED) <= 1.0

    def test_certification_has_highest_max_confidence(self):
        from services.evidence_config import EvidenceSource, get_source_max_confidence, SOURCE_MAX_CONFIDENCE
        cert_max = get_source_max_confidence(EvidenceSource.CERTIFICATION_EARNED)
        for src, max_conf in SOURCE_MAX_CONFIDENCE.items():
            assert cert_max >= max_conf, f"Certification max {cert_max} should be >= {src.value} max {max_conf}"

    def test_all_sources_have_weights(self):
        from services.evidence_config import EvidenceSource, SOURCE_WEIGHTS
        for source in EvidenceSource:
            assert source in SOURCE_WEIGHTS, f"Missing weight for {source}"

    def test_all_sources_have_max_confidence(self):
        from services.evidence_config import EvidenceSource, SOURCE_MAX_CONFIDENCE
        for source in EvidenceSource:
            assert source in SOURCE_MAX_CONFIDENCE, f"Missing max confidence for {source}"

    def test_max_confidence_cap(self):
        from services.evidence_config import MAX_CONFIDENCE_CAP
        assert 0.9 <= MAX_CONFIDENCE_CAP <= 1.0

    def test_diminishing_return_factor(self):
        from services.evidence_config import DIMINISHING_RETURN_FACTOR
        assert 0 < DIMINISHING_RETURN_FACTOR < 1.0


# ─── Skill Normalization Tests ──────────────────────────────────────────────

class TestSkillNormalizationService:

    def setup_method(self):
        from services.skill_normalization_service import SkillNormalizationService
        self.service = SkillNormalizationService()

    def test_normalize_exact_match(self):
        result = self.service.normalize("Python")
        assert result == "Python"

    def test_normalize_case_insensitive(self):
        result = self.service.normalize("python")
        assert result == "Python"

    def test_normalize_alias_js(self):
        result = self.service.normalize("JS")
        assert result == "JavaScript"

    def test_normalize_alias_k8s(self):
        result = self.service.normalize("K8s")
        assert result == "Kubernetes"

    def test_normalize_alias_tf(self):
        result = self.service.normalize("TF")
        assert result == "Terraform"

    def test_normalize_alias_siem(self):
        result = self.service.normalize("SIEM solutions")
        assert result == "SIEM"

    def test_normalize_unknown_returns_none(self):
        result = self.service.normalize("Quantum Computing")
        assert result is None

    def test_normalize_empty_returns_none(self):
        assert self.service.normalize("") is None
        assert self.service.normalize("  ") is None

    def test_normalize_none_returns_none(self):
        assert self.service.normalize(None) is None

    def test_get_skill_data(self):
        data = self.service.get_skill_data("Python")
        assert data is not None
        assert data["name"] == "Python"
        assert data["category"] == "Programming"

    def test_get_skill_data_unknown(self):
        assert self.service.get_skill_data("Unknown Skill") is None

    def test_get_all_canonical_names(self):
        names = self.service.get_all_canonical_names()
        assert len(names) > 50
        assert "Python" in names
        assert "JavaScript" in names
        assert "Kubernetes" in names

    def test_batch_normalize(self):
        results = self.service.batch_normalize(["Python", "JS", "K8s", "Unknown"])
        assert results["Python"] == "Python"
        assert results["JS"] == "JavaScript"
        assert results["K8s"] == "Kubernetes"
        assert results["Unknown"] is None


# ─── Aggregation Service Tests ──────────────────────────────────────────────

class TestSkillEvidenceAggregationService:

    def setup_method(self):
        from services.skill_evidence_aggregation_service import SkillEvidenceAggregationService
        self.service = SkillEvidenceAggregationService()

    def test_empty_evidence_returns_empty(self):
        results = self.service.aggregate([])
        assert results == {}

    def test_single_resume_claim(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource

        items = [
            EvidenceItem(
                skill_name="Python",
                source=EvidenceSource.RESUME_CLAIM,
                confidence=0.5,
            )
        ]
        results = self.service.aggregate(items)
        assert "Python" in results
        assert results["Python"].confidence > 0
        assert results["Python"].confidence_level in ("minimal", "low", "medium", "high")

    def test_multiple_sources_increase_confidence(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource

        items = [
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
            EvidenceItem(skill_name="Python", source=EvidenceSource.GITHUB_LANGUAGE, confidence=0.6),
            EvidenceItem(skill_name="Python", source=EvidenceSource.ASSESSMENT_MATCHED, confidence=0.5),
        ]
        results = self.service.aggregate(items)
        assert "Python" in results
        assert results["Python"].evidence_count == 3
        assert results["Python"].confidence > 0.15

    def test_diminishing_returns(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource

        single_items = [
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
        ]
        single_result = self.service.aggregate(single_items)
        single_conf = single_result["Python"].confidence

        multi_items = [
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
        ]
        multi_result = self.service.aggregate(multi_items)
        multi_conf = multi_result["Python"].confidence

        assert multi_conf < single_conf * 5, "Diminishing returns should prevent linear scaling"

    def test_source_cap_respected(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource, get_source_max_confidence

        items = [
            EvidenceItem(
                skill_name="Python",
                source=EvidenceSource.RESUME_CLAIM,
                confidence=1.0,
            )
        ]
        results = self.service.aggregate(items)
        max_conf = get_source_max_confidence(EvidenceSource.RESUME_CLAIM)
        assert results["Python"].confidence <= max_conf + 0.01

    def test_unknown_skill_filtered(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource

        items = [
            EvidenceItem(skill_name="Quantum Computing", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
        ]
        results = self.service.aggregate(items)
        assert len(results) == 0

    def test_confidence_level_mapping(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource

        cert_items = [
            EvidenceItem(skill_name="Python", source=EvidenceSource.CERTIFICATION_EARNED, confidence=0.9),
            EvidenceItem(skill_name="Python", source=EvidenceSource.ASSESSMENT_COMPLETED, confidence=0.9),
            EvidenceItem(skill_name="Python", source=EvidenceSource.PROJECT_COMPLETED, confidence=0.9),
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_EXPERIENCE, confidence=0.9),
            EvidenceItem(skill_name="Python", source=EvidenceSource.ASSESSMENT_MATCHED, confidence=0.9),
        ]
        results = self.service.aggregate(cert_items)
        assert results["Python"].confidence_level in ("high", "medium")

        minimal_items = [
            EvidenceItem(skill_name="Python", source=EvidenceSource.GITHUB_README, confidence=0.1),
        ]
        results = self.service.aggregate(minimal_items)
        assert results["Python"].confidence_level in ("minimal", "low")

    def test_strongest_source_tracking(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource

        items = [
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.3),
            EvidenceItem(skill_name="Python", source=EvidenceSource.CERTIFICATION_EARNED, confidence=0.9),
        ]
        results = self.service.aggregate(items)
        assert results["Python"].strongest_source == "certification_earned"

    def test_multiple_skills(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource

        items = [
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
            EvidenceItem(skill_name="JavaScript", source=EvidenceSource.GITHUB_LANGUAGE, confidence=0.6),
            EvidenceItem(skill_name="Docker", source=EvidenceSource.ASSESSMENT_MATCHED, confidence=0.5),
        ]
        results = self.service.aggregate(items)
        assert len(results) == 3
        assert "Python" in results
        assert "JavaScript" in results
        assert "Docker" in results

    def test_category_populated_from_knowledge(self):
        from services.skill_evidence_aggregation_service import EvidenceItem
        from services.evidence_config import EvidenceSource

        items = [
            EvidenceItem(skill_name="Python", source=EvidenceSource.RESUME_CLAIM, confidence=0.5),
        ]
        results = self.service.aggregate(items)
        assert results["Python"].category == "Programming"


# ─── Skill Evidence Orchestrator Tests ──────────────────────────────────────

class TestSkillEvidenceOrchestrator:

    def test_orchestrator_instantiation(self):
        from services.skill_evidence_orchestrator import SkillEvidenceOrchestrator
        svc = SkillEvidenceOrchestrator()
        assert svc is not None

    def test_collect_resume_evidence_empty(self):
        from services.skill_evidence_orchestrator import SkillEvidenceOrchestrator
        svc = SkillEvidenceOrchestrator()
        items = svc._collect_resume_evidence("nonexistent-user-id")
        assert items == []

    def test_collect_github_evidence_empty(self):
        from services.skill_evidence_orchestrator import SkillEvidenceOrchestrator
        svc = SkillEvidenceOrchestrator()
        items = svc._collect_github_evidence("nonexistent-user-id")
        assert items == []

    def test_collect_assessment_evidence_empty(self):
        from services.skill_evidence_orchestrator import SkillEvidenceOrchestrator
        svc = SkillEvidenceOrchestrator()
        items = svc._collect_assessment_evidence("nonexistent-user-id")
        assert items == []

    def test_analyze_user_empty(self):
        from services.skill_evidence_orchestrator import SkillEvidenceOrchestrator
        svc = SkillEvidenceOrchestrator()
        results = svc.analyze_user("nonexistent-user-id")
        assert results == {}

    def test_get_evidence_summary(self):
        from services.skill_evidence_orchestrator import SkillEvidenceOrchestrator
        from services.skill_evidence_aggregation_service import AggregatedSkillEvidence
        svc = SkillEvidenceOrchestrator()

        mock_results = {
            "Python": AggregatedSkillEvidence(
                skill_id="python", skill_name="Python", category="Programming",
                confidence=0.75, confidence_level="high", sources=[], evidence_count=3,
                strongest_source="certification_earned",
            ),
            "JavaScript": AggregatedSkillEvidence(
                skill_id="javascript", skill_name="JavaScript", category="Programming",
                confidence=0.30, confidence_level="low", sources=[], evidence_count=1,
                strongest_source="github_language",
            ),
        }
        summary = svc.get_evidence_summary(mock_results)
        assert summary["total_skills"] == 2
        assert summary["high_confidence"] == 1
        assert summary["low_confidence"] == 1


# ─── Schema Validation Tests ───────────────────────────────────────────────

class TestSkillEvidenceSchemas:

    def test_skill_evidence_item_schema(self):
        from schemas.skill_evidence import SkillEvidenceItem
        item = SkillEvidenceItem(
            skill_id="python",
            skill_name="Python",
            category="Programming",
            confidence=0.75,
            confidence_level="high",
            sources=[],
            evidence_count=3,
            strongest_source="certification_earned",
        )
        assert item.skill_id == "python"
        assert item.confidence == 0.75

    def test_skill_evidence_summary_schema(self):
        from schemas.skill_evidence import SkillEvidenceSummary
        summary = SkillEvidenceSummary(
            total_skills=10,
            high_confidence=3,
            medium_confidence=4,
            low_confidence=2,
            minimal_confidence=1,
            skills=[],
        )
        assert summary.total_skills == 10

    def test_evidence_source_detail_schema(self):
        from schemas.skill_evidence import EvidenceSourceDetail
        detail = EvidenceSourceDetail(
            source="resume_claim",
            raw_confidence=0.5,
            effective_confidence=0.4,
            weight=0.15,
            contribution=0.06,
        )
        assert detail.source == "resume_claim"
