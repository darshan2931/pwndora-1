import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.certification_planner_service import certification_planner_service


class TestCertificationPlannerService:
    def test_plan_soc_analyst_has_expected_certs(self):
        plan = certification_planner_service.build_plan("SOC Analyst", study_hours_per_week=10)
        names = [c["name"] for c in plan["certifications"]]
        assert "CompTIA Security+" in names
        assert "Blue Team Level 1" in names
        assert plan["summary"]["total_certifications"] > 0
        assert plan["summary"]["weekly_study_hours"] == 10.0

    def test_prerequisite_order_is_respected(self):
        plan = certification_planner_service.build_plan("Penetration Tester", study_hours_per_week=10)
        positions = {c["name"]: c["position"] for c in plan["certifications"]}
        if "eJPT" in positions and "PNPT" in positions:
            assert positions["eJPT"] < positions["PNPT"]
        if "PNPT" in positions and "OSCP" in positions:
            assert positions["PNPT"] < positions["OSCP"]

    def test_cost_is_positive_and_summary_consistent(self):
        plan = certification_planner_service.build_plan("Security Architect", study_hours_per_week=15)
        total = sum(c["cost"]["total"] for c in plan["certifications"])
        assert abs(total - plan["summary"]["total_cost"]) < 0.01
        assert plan["summary"]["total_cost"] > 0

    def test_completed_certs_are_excluded(self):
        plan = certification_planner_service.build_plan(
            "Penetration Tester",
            study_hours_per_week=10,
            completed_certifications=["eJPT"],
        )
        names = [c["name"] for c in plan["certifications"]]
        assert "eJPT" not in names

    def test_unknown_role_returns_empty_plan(self):
        plan = certification_planner_service.build_plan("Not A Real Role", study_hours_per_week=10)
        assert plan["certifications"] == []
        assert plan["summary"]["total_certifications"] == 0

    def test_weekly_hours_floor(self):
        plan = certification_planner_service.build_plan("SOC Analyst", study_hours_per_week=0)
        assert plan["summary"]["weekly_study_hours"] == 1.0

    def test_each_cert_has_required_fields(self):
        plan = certification_planner_service.build_plan("SOC Analyst", study_hours_per_week=10)
        for cert in plan["certifications"]:
            assert cert["name"]
            assert cert["weeks"] > 0
            assert "total" in cert["cost"]
            assert cert["position"] >= 1
            assert cert["start_week"] >= 0
            assert cert["end_week"] >= cert["start_week"]