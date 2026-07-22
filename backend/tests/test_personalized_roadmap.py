import os
import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock


# ─── Personalized Roadmap Service Tests ─────────────────────────────────────

class TestPersonalizedRoadmapService:

    def setup_method(self):
        from services.personalized_roadmap_service import PersonalizedRoadmapService
        self.service = PersonalizedRoadmapService()

    def test_build_dependency_graph(self):
        role_data = {
            "role": "SOC Analyst",
            "required_skills": ["SIEM", "Networking"],
        }
        graph = self.service._build_dependency_graph(role_data)
        assert "SIEM" in graph
        assert "Networking" in graph
        assert isinstance(graph["SIEM"], list)

    def test_detect_circular_dependencies_no_cycle(self):
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": [],
        }
        cycles = self.service._detect_circular_dependencies(graph)
        assert len(cycles) == 0

    def test_detect_circular_dependencies_with_cycle(self):
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }
        cycles = self.service._detect_circular_dependencies(graph)
        assert len(cycles) > 0

    def test_determine_required_learning(self):
        role_data = {
            "required_skills": ["SIEM", "Networking"],
        }
        skill_confidences = {
            "SIEM": 0.8,
            "Networking": 0.2,
        }
        dependency_graph = {
            "SIEM": ["Networking"],
            "Networking": [],
        }
        required = self.service._determine_required_learning(
            role_data, skill_confidences, dependency_graph
        )
        assert "Networking" in required
        assert "SIEM" not in required

    def test_topological_sort_with_evidence(self):
        required_learning = {"A", "B", "C"}
        dependency_graph = {
            "A": ["B"],
            "B": ["C"],
            "C": [],
        }
        skill_confidences = {"A": 0.5, "B": 0.3, "C": 0.8}
        sorted_skills = self.service._topological_sort_with_evidence(
            required_learning, dependency_graph, skill_confidences
        )
        assert len(sorted_skills) == 3
        assert sorted_skills.index("C") < sorted_skills.index("B")
        assert sorted_skills.index("B") < sorted_skills.index("A")

    def test_create_skill_nodes(self):
        sorted_skills = ["Networking", "SIEM"]
        skill_confidences = {"Networking": 0.3, "SIEM": 0.0}
        dependency_graph = {
            "SIEM": ["Networking"],
            "Networking": [],
        }
        nodes = self.service._create_skill_nodes(
            sorted_skills, skill_confidences, dependency_graph
        )
        assert len(nodes) == 2
        assert nodes[0]["title"] == "Networking"
        assert nodes[1]["title"] == "SIEM"
        assert nodes[1]["prerequisites"] == ["skill-networking"]

    def test_create_skill_nodes_has_required_fields(self):
        sorted_skills = ["Linux"]
        skill_confidences = {}
        dependency_graph = {"Linux": []}
        nodes = self.service._create_skill_nodes(
            sorted_skills, skill_confidences, dependency_graph
        )
        assert len(nodes) == 1
        node = nodes[0]
        assert "id" in node
        assert "title" in node
        assert "description" in node
        assert "type" in node
        assert "status" in node
        assert "estimatedHours" in node
        assert "difficulty" in node
        assert "skills" in node
        assert "prerequisites" in node
        assert "resources" in node

    def test_assign_node_statuses_all_available(self):
        nodes = [
            {"id": "skill-a", "title": "A", "type": "skill", "status": "locked", "prerequisites": [], "skills": ["A"]},
            {"id": "skill-b", "title": "B", "type": "skill", "status": "locked", "prerequisites": ["skill-a"], "skills": ["B"]},
        ]
        skill_confidences = {"A": 0.0, "B": 0.0}
        result = self.service._assign_node_statuses(nodes, skill_confidences)
        assert result[0]["status"] == "available"
        assert result[1]["status"] == "locked"

    def test_assign_node_statuses_completed_prereq(self):
        nodes = [
            {"id": "skill-a", "title": "A", "type": "skill", "status": "completed", "prerequisites": [], "skills": ["A"]},
            {"id": "skill-b", "title": "B", "type": "skill", "status": "locked", "prerequisites": ["skill-a"], "skills": ["B"]},
        ]
        skill_confidences = {"A": 0.8, "B": 0.0}
        result = self.service._assign_node_statuses(nodes, skill_confidences)
        assert result[0]["status"] == "completed"
        assert result[1]["status"] == "available"

    def test_assign_node_statuses_high_confidence(self):
        nodes = [
            {"id": "skill-a", "title": "A", "type": "skill", "status": "locked", "prerequisites": [], "skills": ["A"]},
        ]
        skill_confidences = {"A": 0.7}
        result = self.service._assign_node_statuses(nodes, skill_confidences)
        assert result[0]["status"] == "completed"

    def test_group_into_phases(self):
        nodes = [
            {"id": "step-0", "title": "Linux", "type": "skill", "estimatedHours": 10},
            {"id": "step-1", "title": "Networking", "type": "skill", "estimatedHours": 15},
            {"id": "step-2", "title": "Project", "type": "project", "estimatedHours": 8},
        ]
        role_data = {"role": "SOC Analyst"}
        phases = self.service._group_into_phases(nodes, role_data)
        assert len(phases) > 0
        for phase in phases:
            assert "id" in phase
            assert "name" in phase
            assert "totalHours" in phase

    def test_unlock_dependents(self):
        nodes = [
            {"id": "skill-a", "title": "A", "type": "skill", "status": "in-progress", "prerequisites": [], "skills": ["A"]},
            {"id": "skill-b", "title": "B", "type": "skill", "status": "locked", "prerequisites": ["skill-a"], "skills": ["B"]},
        ]
        self.service._unlock_dependents(nodes, 0)
        assert nodes[1]["status"] == "available"

    @patch('services.personalized_roadmap_service.SkillEvidenceRepository')
    def test_load_skill_confidences(self, mock_repo_cls):
        mock_ev = MagicMock()
        mock_ev.skill_id = "SIEM"
        mock_ev.confidence = 75
        mock_instance = MagicMock()
        mock_instance.get_by_user_id.return_value = [mock_ev]
        self.service.evidence_repo = mock_instance

        confidences = self.service._load_skill_confidences("user-123")
        assert "SIEM" in confidences
        assert confidences["SIEM"] == 0.75

    @patch('services.personalized_roadmap_service.SkillEvidenceRepository')
    def test_load_skill_confidences_empty(self, mock_repo_cls):
        mock_instance = MagicMock()
        mock_instance.get_by_user_id.return_value = []
        self.service.evidence_repo = mock_instance

        confidences = self.service._load_skill_confidences("user-123")
        assert confidences == {}


# ─── Roadmap Explanation Service Tests ──────────────────────────────────────

class TestRoadmapExplanationService:

    def test_fallback_explanation_high_readiness(self):
        from app.ai.roadmap_explanation import RoadmapExplanationService
        service = RoadmapExplanationService()
        result = service._fallback_explanation(
            "SOC Analyst", 0.8, [], [], {}
        )
        assert "overview" in result
        assert len(result["first_steps"]) > 0
        assert len(result["milestones"]) > 0

    def test_fallback_explanation_low_readiness(self):
        from app.ai.roadmap_explanation import RoadmapExplanationService
        service = RoadmapExplanationService()
        nodes = [
            {"title": "Linux", "type": "skill", "estimatedHours": 10},
            {"title": "Networking", "type": "skill", "estimatedHours": 15},
        ]
        phases = [
            {"name": "Phase 1: Operating Systems", "skillCount": 1},
        ]
        result = service._fallback_explanation(
            "SOC Analyst", 0.1, nodes, phases, {}
        )
        assert "overview" in result
        assert "SOC Analyst" in result["overview"]

    def test_parse_valid_json(self):
        from app.ai.roadmap_explanation import RoadmapExplanationService
        service = RoadmapExplanationService()
        result = service._parse_explanation('{"overview": "test", "phase_highlights": [], "first_steps": [], "milestones": [], "personalization_notes": "test"}')
        assert result is not None
        assert result["overview"] == "test"

    def test_parse_invalid_json(self):
        from app.ai.roadmap_explanation import RoadmapExplanationService
        service = RoadmapExplanationService()
        result = service._parse_explanation("not json")
        assert result is None


# ─── Schema Validation Tests ────────────────────────────────────────────────

class TestRoadmapSchemas:

    def test_roadmap_node_has_all_fields(self):
        node = {
            "id": "step-0",
            "title": "Linux",
            "description": "Learn Linux",
            "type": "skill",
            "status": "available",
            "estimatedHours": 10,
            "difficulty": "Beginner",
            "skills": ["Linux"],
            "prerequisites": [],
            "resources": [],
        }
        assert node["id"] == "step-0"
        assert node["type"] == "skill"
        assert node["status"] == "available"

    def test_roadmap_phase_has_required_fields(self):
        phase = {
            "id": "phase-1",
            "name": "Phase 1: Foundations",
            "description": "Core skills",
            "nodeRange": [0, 5],
            "totalHours": 60,
            "skillCount": 5,
            "projectCount": 0,
            "certificationCount": 0,
        }
        assert phase["id"] == "phase-1"
        assert phase["nodeRange"] == [0, 5]
