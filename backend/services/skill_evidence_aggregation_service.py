import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

from services.evidence_config import (
    EvidenceSource,
    get_source_weight,
    get_source_max_confidence,
    MAX_CONFIDENCE_CAP,
    DIMINISHING_RETURN_FACTOR,
)
from services.skill_normalization_service import skill_normalizer

logger = logging.getLogger(__name__)


class EvidenceItem:
    def __init__(
        self,
        skill_name: str,
        source: EvidenceSource,
        confidence: float,
        details: Optional[Dict] = None,
        repository: Optional[str] = None,
        evidence_text: Optional[str] = None,
    ):
        self.skill_name = skill_name
        self.source = source
        self.confidence = min(confidence, 1.0)
        self.details = details or {}
        self.repository = repository
        self.evidence_text = evidence_text


class AggregatedSkillEvidence:
    def __init__(
        self,
        skill_id: str,
        skill_name: str,
        category: str,
        confidence: float,
        confidence_level: str,
        sources: List[Dict],
        evidence_count: int,
        strongest_source: Optional[str] = None,
        last_updated: Optional[str] = None,
    ):
        self.skill_id = skill_id
        self.skill_name = skill_name
        self.category = category
        self.confidence = confidence
        self.confidence_level = confidence_level
        self.sources = sources
        self.evidence_count = evidence_count
        self.strongest_source = strongest_source
        self.last_updated = last_updated


class SkillEvidenceAggregationService:

    def aggregate(
        self,
        evidence_items: List[EvidenceItem],
    ) -> Dict[str, AggregatedSkillEvidence]:
        grouped: Dict[str, List[EvidenceItem]] = {}
        for item in evidence_items:
            canonical = skill_normalizer.normalize(item.skill_name)
            if not canonical:
                logger.debug("Skipping unmappable skill: %s", item.skill_name)
                continue
            grouped.setdefault(canonical, []).append(item)

        results: Dict[str, AggregatedSkillEvidence] = {}
        for skill_name, items in grouped.items():
            result = self._aggregate_skill(skill_name, items)
            if result:
                results[skill_name] = result

        return results

    def _aggregate_skill(
        self,
        skill_name: str,
        items: List[EvidenceItem],
    ) -> Optional[AggregatedSkillEvidence]:
        if not items:
            return None

        sorted_items = sorted(items, key=lambda x: get_source_weight(x.source), reverse=True)

        raw_score = 0.0
        source_details: List[Dict] = []
        best_source_confidence = 0.0
        best_source_name = None

        for i, item in enumerate(sorted_items):
            weight = get_source_weight(item.source)
            max_conf = get_source_max_confidence(item.source)

            effective_conf = min(item.confidence, max_conf)

            if i > 0:
                effective_conf *= (DIMINISHING_RETURN_FACTOR ** i)

            contribution = effective_conf * weight
            raw_score += contribution

            source_details.append({
                "source": item.source.value,
                "raw_confidence": round(item.confidence, 3),
                "effective_confidence": round(effective_conf, 3),
                "weight": round(weight, 3),
                "contribution": round(contribution, 3),
                "repository": item.repository,
                "evidence_text": item.evidence_text,
                "details": item.details,
            })

            if effective_conf > best_source_confidence:
                best_source_confidence = effective_conf
                best_source_name = item.source.value

        normalized = min(raw_score, MAX_CONFIDENCE_CAP)

        confidence_level = self._confidence_level(normalized)

        skill_data = skill_normalizer.get_skill_data(skill_name)
        category = skill_data.get("category", "Unknown") if skill_data else "Unknown"

        return AggregatedSkillEvidence(
            skill_id=skill_name.lower().replace(" ", "_"),
            skill_name=skill_name,
            category=category,
            confidence=round(normalized, 3),
            confidence_level=confidence_level,
            sources=source_details,
            evidence_count=len(items),
            strongest_source=best_source_name,
            last_updated=datetime.now(timezone.utc).isoformat(),
        )

    def _confidence_level(self, score: float) -> str:
        if score >= 0.70:
            return "high"
        elif score >= 0.40:
            return "medium"
        elif score >= 0.15:
            return "low"
        else:
            return "minimal"


aggregation_service = SkillEvidenceAggregationService()
