import logging
from typing import List, Dict

from repositories.opportunity_repositories import OpportunityMatchRepository

logger = logging.getLogger(__name__)


class OpportunityPrioritizationService:
    """
    Ranks and prioritizes opportunity matches for display,
    filtering, and recommendation.
    """

    CATEGORY_PRIORITY = {
        "highly_eligible": 4,
        "strong_contender": 3,
        "developing_candidate": 2,
        "early_gap": 1,
    }

    def __init__(self):
        self.match_repo = OpportunityMatchRepository()

    def prioritize_matches(
        self,
        matches: List[Dict],
        sort_by: str = "overall_score",
        category_filter: str = None,
        min_score: int = None,
    ) -> List[Dict]:
        filtered = matches

        if category_filter:
            filtered = [m for m in filtered if m.get("category") == category_filter]

        if min_score is not None:
            filtered = [m for m in filtered if m.get("overall_score", 0) >= min_score]

        if sort_by == "overall_score":
            filtered.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        elif sort_by == "category":
            filtered.sort(
                key=lambda x: self.CATEGORY_PRIORITY.get(x.get("category", ""), 0),
                reverse=True,
            )
        elif sort_by == "skill_coverage":
            filtered.sort(
                key=lambda x: x.get("breakdown", {}).get("required_skill_coverage", 0),
                reverse=True,
            )
        elif sort_by == "gaps":
            filtered.sort(
                key=lambda x: len(x.get("missing_skills", [])),
            )
        else:
            filtered.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

        return filtered

    def get_top_recommendations(
        self,
        matches: List[Dict],
        limit: int = 5,
    ) -> List[Dict]:
        prioritized = self.prioritize_matches(matches, sort_by="overall_score")
        return prioritized[:limit]

    def get_category_summary(self, matches: List[Dict]) -> Dict:
        summary = {
            "highly_eligible": 0,
            "strong_contender": 0,
            "developing_candidate": 0,
            "early_gap": 0,
            "total": len(matches),
        }
        for m in matches:
            cat = m.get("category", "early_gap")
            if cat in summary:
                summary[cat] += 1
        return summary

    def get_readiest_opportunities(
        self,
        matches: List[Dict],
        threshold: int = 60,
    ) -> List[Dict]:
        return [
            m for m in matches
            if m.get("overall_score", 0) >= threshold
        ]

    def rank_by_skill_gap(
        self,
        matches: List[Dict],
    ) -> List[Dict]:
        return sorted(
            matches,
            key=lambda x: len(x.get("missing_skills", [])),
        )
