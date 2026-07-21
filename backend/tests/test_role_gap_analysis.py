import os
import json
import pytest
from unittest.mock import patch, MagicMock


# ─── Gap Config Tests ────────────────────────────────────────────────────────

class TestRoleGapConfig:

    def test_importance_levels_exist(self):
        from services.role_gap_config import SkillImportance
        assert SkillImportance.REQUIRED.value == 0.9
        assert SkillImportance.CRITICAL.value == 0.7
        assert SkillImportance.IMPORTANT.value == 0.5
        assert SkillImportance.BENEFICIAL.value == 0.3

    def test_minimum_confidence_levels(self):
        from services.role_gap_config import MinimumConfidence
        assert MinimumConfidence.REQUIRED.value == 0.80
        assert MinimumConfidence.CRITICAL.value == 0.65
        assert MinimumConfidence.IMPORTANT.value == 0.50
        assert MinimumConfidence.BENEFICIAL.value == 0.30

    def test_gap_status_values(self):
        from services.role_gap_config import GapStatus
        statuses = [s.value for s in GapStatus]
        assert "covered" in statuses
        assert "missing" in statuses
        assert "critical" in statuses
        assert "partial" in statuses
        assert "minimal" in statuses

    def test_get_importance_level_for_known_role(self):
        from services.role_gap_config import get_importance_level, SkillImportance
        importance = get_importance_level("SOC Analyst", "SIEM", is_required=True)
        assert importance == SkillImportance.REQUIRED

    def test_get_importance_level_fallback(self):
        from services.role_gap_config import get_importance_level, SkillImportance
        importance = get_importance_level("Unknown Role", "unknown_skill", is_required=True)
        assert importance == SkillImportance.IMPORTANT

    def test_get_minimum_confidence_matches_importance(self):
        from services.role_gap_config import get_importance_level, get_minimum_confidence, SkillImportance, MinimumConfidence
        importance = get_importance_level("SOC Analyst", "SIEM", is_required=True)
        min_conf = get_minimum_confidence("SOC Analyst", "SIEM", is_required=True)
        assert min_conf == MinimumConfidence.REQUIRED.value

    def test_get_importance_score_returns_float(self):
        from services.role_gap_config import get_importance_score
        score = get_importance_score("SOC Analyst", "SIEM", is_required=True)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_all_roles_have_configs(self):
        from services.role_gap_config import ROLE_SKILL_CONFIGS
        expected_roles = [
            "SOC Analyst", "Penetration Tester", "Cloud Security Engineer",
            "Application Security Engineer", "Digital Forensics Analyst",
            "Threat Intelligence Analyst", "Security Architect",
            "DevSecOps Engineer", "GRC Analyst", "Incident Responder",
        ]
        for role in expected_roles:
            assert role in ROLE_SKILL_CONFIGS, f"Missing config for {role}"
            assert "required_skills" in ROLE_SKILL_CONFIGS[role]
            assert "optional_skills" in ROLE_SKILL_CONFIGS[role]


# ─── Role Adapter Tests ─────────────────────────────────────────────────────

class TestRoleAdapter:

    def setup_method(self):
        from services.role_adapter import RoleAdapter
        self.adapter = RoleAdapter()

    def test_get_role_enriched_returns_role(self):
        result = self.adapter.get_role_enriched("SOC Analyst")
        assert result is not None
        assert result["role_name"] == "SOC Analyst"

    def test_get_role_enriched_has_required_skills(self):
        result = self.adapter.get_role_enriched("SOC Analyst")
        assert len(result["required_skills"]) > 0
        for skill in result["required_skills"]:
            assert "skill_name" in skill
            assert "importance" in skill
            assert "importance_score" in skill
            assert "minimum_confidence" in skill
            assert "is_required" in skill

    def test_get_role_enriched_has_optional_skills(self):
        result = self.adapter.get_role_enriched("SOC Analyst")
        assert len(result["optional_skills"]) > 0

    def test_get_role_enriched_nonexistent(self):
        result = self.adapter.get_role_enriched("Nonexistent Role")
        assert result is None

    def test_get_all_roles_enriched(self):
        results = self.adapter.get_all_roles_enriched()
        assert len(results) >= 10
        for role in results:
            assert "role_id" in role
            assert "role_name" in role
            assert "required_skills" in role

    def test_get_skill_importance_for_role(self):
        score = self.adapter.get_skill_importance_for_role("SOC Analyst", "SIEM")
        assert 0.0 <= score <= 1.0
        assert score > 0.5

    def test_get_skill_importance_unknown_role(self):
        score = self.adapter.get_skill_importance_for_role("Unknown", "unknown_skill")
        assert score == 0.5

    def test_get_min_confidence_for_role(self):
        min_conf = self.adapter.get_min_confidence_for_role("SOC Analyst", "SIEM")
        assert 0.0 <= min_conf <= 1.0
        assert min_conf >= 0.65


# ─── Gap Analysis Service Tests ─────────────────────────────────────────────

class TestGapAnalysisService:

    def setup_method(self):
        from services.gap_analysis_service import GapAnalysisService
        self.service = GapAnalysisService()

    def test_calculate_skill_gap_covers_skill(self):
        gap = self.service.calculate_skill_gap("SOC Analyst", "siem", 0.9, is_required=True)
        assert gap["gap_status"] == "covered"
        assert gap["gap_size"] == 0.0

    def test_calculate_skill_gap_missing_skill(self):
        gap = self.service.calculate_skill_gap("SOC Analyst", "siem", 0.0, is_required=True)
        assert gap["gap_status"] == "missing"
        assert gap["gap_size"] > 0.0

    def test_calculate_skill_gap_partial_skill(self):
        gap = self.service.calculate_skill_gap("SOC Analyst", "siem", 0.4, is_required=True)
        assert gap["gap_status"] in ("partial", "minimal", "missing")

    def test_calculate_skill_gap_has_importance(self):
        gap = self.service.calculate_skill_gap("SOC Analyst", "siem", 0.5, is_required=True)
        assert "importance" in gap
        assert "importance_score" in gap
        assert gap["is_required"] is True

    def test_calculate_skill_gap_has_category(self):
        gap = self.service.calculate_skill_gap("SOC Analyst", "siem", 0.5, is_required=True)
        assert "category" in gap
        assert isinstance(gap["category"], str)

    def test_calculate_priority_score(self):
        gap = self.service.calculate_skill_gap("SOC Analyst", "siem", 0.0, is_required=True)
        priority = self.service.calculate_priority_score(gap)
        assert 0.0 <= priority <= 1.0

    def test_calculate_priority_score_high_for_critical_gap(self):
        gap = self.service.calculate_skill_gap("SOC Analyst", "siem", 0.0, is_required=True)
        gap["importance_score"] = 0.9
        gap["gap_size"] = 0.8
        priority = self.service.calculate_priority_score(gap)
        assert priority > 0.5

    def test_calculate_readiness_all_covered(self):
        confidences = {
            "SIEM": 0.9,
            "Incident Response": 0.85,
            "Networking": 0.8,
            "Log Analysis": 0.75,
            "MITRE ATT&CK": 0.7,
            "Linux": 0.6,
            "Windows": 0.6,
        }
        result = self.service.calculate_readiness("SOC Analyst", confidences)
        assert result["overall_readiness"] > 0.5
        assert len(result["required_skills"]) > 0

    def test_calculate_readiness_no_skills(self):
        result = self.service.calculate_readiness("SOC Analyst", {})
        assert result["overall_readiness"] == 0.0

    def test_determine_readiness_level(self):
        assert self.service.determine_readiness_level(0.9) == "excellent"
        assert self.service.determine_readiness_level(0.75) == "good"
        assert self.service.determine_readiness_level(0.55) == "developing"
        assert self.service.determine_readiness_level(0.3) == "beginning"
        assert self.service.determine_readiness_level(0.1) == "not_started"

    def test_get_learning_path_for_role(self):
        path = self.service.get_learning_path_for_role("SOC Analyst")
        assert len(path) > 0
        for step in path:
            assert "skill_id" in step
            assert "order" in step

    def test_get_learning_path_nonexistent_role(self):
        path = self.service.get_learning_path_for_role("Nonexistent Role")
        assert path == []

    def test_find_next_skill(self):
        confidences = {"SIEM": 0.0}
        next_skill = self.service.find_next_skill("SOC Analyst", confidences)
        assert next_skill is not None
        assert "skill_id" in next_skill
        assert "priority_score" in next_skill
        assert "recommendation_reason" in next_skill

    def test_find_next_skill_all_covered(self):
        confidences = {
            "SIEM": 0.9,
            "Incident Response": 0.9,
            "Networking": 0.9,
            "Log Analysis": 0.9,
            "MITRE ATT&CK": 0.9,
            "Linux": 0.9,
            "Windows": 0.9,
            "Python": 0.9,
            "Bash": 0.9,
            "PowerShell": 0.9,
            "EDR": 0.9,
        }
        next_skill = self.service.find_next_skill("SOC Analyst", confidences)
        assert next_skill is None

    def test_check_prerequisites_met(self):
        met, blockers = self.service.check_prerequisites_met("SIEM", set())
        assert isinstance(met, bool)
        assert isinstance(blockers, list)

    def test_topological_sort_skills(self):
        sorted_skills = self.service._topological_sort_skills(["SIEM", "Networking"])
        assert len(sorted_skills) == 2
        assert "SIEM" in sorted_skills
        assert "Networking" in sorted_skills


# ─── Role Gap Analysis Service Tests ────────────────────────────────────────

class TestRoleGapAnalysisService:

    def setup_method(self):
        from services.role_gap_analysis_service import RoleGapAnalysisService
        self.service = RoleGapAnalysisService()

    @patch('services.role_gap_analysis_service.SkillEvidenceRepository')
    def test_analyze_role_gap_no_evidence(self, mock_repo_cls):
        mock_instance = MagicMock()
        mock_instance.get_by_user_id.return_value = []
        self.service._skill_evidence_repo = mock_instance
        result = self.service.analyze_role_gap("user-123", "SOC Analyst")
        assert "role_id" in result
        assert result["role_id"] == "SOC Analyst"
        assert "readiness_score" in result
        assert "skill_gaps" in result
        assert "priority_breakdown" in result
        assert "learning_path" in result

    @patch('services.role_gap_analysis_service.SkillEvidenceRepository')
    def test_analyze_role_gap_with_evidence(self, mock_repo_cls):
        mock_ev = MagicMock()
        mock_ev.skill_id = "SIEM"
        mock_ev.confidence = 75
        mock_instance = MagicMock()
        mock_instance.get_by_user_id.return_value = [mock_ev]
        self.service._skill_evidence_repo = mock_instance

        result = self.service.analyze_role_gap("user-123", "SOC Analyst")
        assert result["role_id"] == "SOC Analyst"
        assert result["readiness_score"] > 0
        assert len(result["skill_gaps"]) > 0

    def test_analyze_role_gap_nonexistent_role(self):
        result = self.service.analyze_role_gap("user-123", "Nonexistent Role")
        assert "error" in result

    def test_build_skill_gaps(self):
        from services.gap_analysis_service import GapAnalysisService
        from services.role_adapter import RoleAdapter
        role_adapter = RoleAdapter()
        gap_service = GapAnalysisService(role_adapter=role_adapter)
        from services.role_gap_analysis_service import RoleGapAnalysisService
        service = RoleGapAnalysisService(
            gap_analysis_service=gap_service,
            role_adapter=role_adapter,
        )

        readiness = {
            "required_skills": {
                "SIEM": {"confidence": 0.0, "importance": "required", "importance_score": 0.9, "minimum_confidence": 0.8},
            },
            "optional_skills": {},
        }
        gaps = service._build_skill_gaps("SOC Analyst", {"SIEM": 0.0}, readiness)
        assert len(gaps) > 0
        assert gaps[0]["skill_id"] == "SIEM"
        assert "priority_score" in gaps[0]
        assert "priority_level" in gaps[0]

    def test_determine_priority_level(self):
        from services.role_gap_analysis_service import RoleGapAnalysisService
        service = RoleGapAnalysisService()
        assert service._determine_priority_level(0.8) == "highest"
        assert service._determine_priority_level(0.6) == "high"
        assert service._determine_priority_level(0.4) == "medium"
        assert service._determine_priority_level(0.2) == "low"

    def test_build_priority_breakdown(self):
        from services.role_gap_analysis_service import RoleGapAnalysisService
        service = RoleGapAnalysisService()
        gaps = [
            {"priority_level": "highest", "skill_id": "a"},
            {"priority_level": "high", "skill_id": "b"},
            {"priority_level": "medium", "skill_id": "c"},
            {"priority_level": "low", "skill_id": "d"},
        ]
        breakdown = service._build_priority_breakdown(gaps)
        assert len(breakdown["highest"]) == 1
        assert len(breakdown["high"]) == 1
        assert len(breakdown["medium"]) == 1
        assert len(breakdown["low"]) == 1

    def test_save_and_load_analysis(self):
        mock_ev_instance = MagicMock()
        mock_ev_instance.get_by_user_id.return_value = []
        self.service._skill_evidence_repo = mock_ev_instance

        mock_analysis = MagicMock()
        mock_analysis.role_id = "SOC Analyst"
        mock_analysis.role_name = "SOC Analyst"
        mock_analysis.readiness_score = 45
        mock_analysis.readiness_level = "developing"
        mock_analysis.total_skills = 5
        mock_analysis.covered_count = 1
        mock_analysis.partial_count = 1
        mock_analysis.missing_count = 3
        mock_analysis.skill_gaps = []
        mock_analysis.priority_breakdown = {}
        mock_analysis.recommended_next_skill = None
        mock_analysis.learning_path = []
        mock_analysis.ai_explanation = None
        mock_analysis.analyzed_at = MagicMock()
        mock_analysis.analyzed_at.isoformat.return_value = "2026-07-22T00:00:00"
        mock_role_instance = MagicMock()
        mock_role_instance.get_by_user_and_role.return_value = None
        mock_role_instance.create.return_value = mock_analysis
        self.service._role_analysis_repo = mock_role_instance

        result = self.service.analyze_role_gap("user-123", "SOC Analyst")
        saved = self.service.save_analysis("user-123", result)
        assert saved is not None


# ─── AI Explanation Tests ──────────────────────────────────────────────────

class TestGapExplanationService:

    def test_fallback_explanation_high_readiness(self):
        from app.ai.gap_explanation import GapExplanationService
        service = GapExplanationService()
        result = service._fallback_explanation("SOC Analyst", 0.9, [])
        assert result["summary"] != ""
        assert len(result["strengths"]) > 0
        assert len(result["action_plan"]) > 0

    def test_fallback_explanation_low_readiness(self):
        from app.ai.gap_explanation import GapExplanationService
        service = GapExplanationService()
        gaps = [
            {"skill_name": "siem", "gap_status": "missing"},
            {"skill_name": "incident_response", "gap_status": "critical"},
        ]
        result = service._fallback_explanation("SOC Analyst", 0.1, gaps)
        assert "SOC Analyst" in result["summary"]
        assert len(result["critical_gaps"]) > 0

    def test_parse_valid_json(self):
        from app.ai.gap_explanation import GapExplanationService
        service = GapExplanationService()
        result = service._parse_explanation('{"summary": "test", "strengths": [], "critical_gaps": [], "action_plan": [], "estimated_timeline": "4 weeks", "encouragement": "Good"}')
        assert result is not None
        assert result["summary"] == "test"

    def test_parse_invalid_json(self):
        from app.ai.gap_explanation import GapExplanationService
        service = GapExplanationService()
        result = service._parse_explanation("not json at all")
        assert result is None

    def test_parse_json_with_code_blocks(self):
        from app.ai.gap_explanation import GapExplanationService
        service = GapExplanationService()
        result = service._parse_explanation('```\n{"summary": "test"}\n```')
        assert result is not None
        assert result["summary"] == "test"


# ─── Schema Tests ──────────────────────────────────────────────────────────

class TestSchemas:

    def test_skill_gap_schema(self):
        from schemas.role_gap_analysis import SkillGap
        gap = SkillGap(
            skill_id="SIEM",
            skill_name="SIEM",
            category="Defensive Security",
            confidence=0.5,
            minimum_confidence=0.8,
            gap_size=0.3,
            gap_status="partial",
            importance="critical",
            importance_score=0.7,
            is_required=True,
            has_prerequisites=False,
            blocked_by=[],
            unblocked_skills=[],
            priority_score=0.6,
            priority_level="high",
            evidence_sources=[],
            recommendation_reason="Test reason",
        )
        assert gap.skill_id == "SIEM"
        assert gap.gap_size == 0.3

    def test_role_gap_analysis_result_schema(self):
        from schemas.role_gap_analysis import RoleGapAnalysisResult, SkillGap, PriorityCategory
        result = RoleGapAnalysisResult(
            role_id="SOC Analyst",
            role_name="SOC Analyst",
            role_description="Test",
            readiness_score=0.5,
            readiness_level="developing",
            total_skills=5,
            covered_count=2,
            partial_count=1,
            missing_count=2,
            skill_gaps=[],
            priority_breakdown=PriorityCategory(),
            learning_path=[],
        )
        assert result.role_id == "SOC Analyst"
        assert result.total_skills == 5

    def test_next_skill_recommendation_schema(self):
        from schemas.role_gap_analysis import NextSkillRecommendation
        rec = NextSkillRecommendation(
            skill_id="SIEM",
            skill_name="SIEM",
            category="Defensive Security",
            confidence=0.3,
            gap_size=0.5,
            importance="required",
            priority_score=0.8,
            prerequisites_met=True,
            blockers=[],
            recommendation_reason="High priority gap",
        )
        assert rec.skill_id == "SIEM"
        assert rec.gap_size == 0.5
