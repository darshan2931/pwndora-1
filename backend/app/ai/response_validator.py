import re
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Validates and sanitizes AI responses."""
    
    @staticmethod
    def validate_json(text: str) -> Optional[dict]:
        """Attempts to parse JSON from a raw string, stripping markdown if present."""
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning("Failed to validate JSON: %s", e)
            return None


class ResponseParser:
    """Parses raw dictionary responses into structured outputs."""
    
    @staticmethod
    def parse_resume_skills(data: Any) -> dict:
        result = {"skills": [], "projects": [], "certifications": [], "education": []}
        if isinstance(data, dict):
            result["skills"] = [str(s) for s in data.get("skills", [])]
            result["projects"] = [str(p) for p in data.get("projects", [])]
            result["certifications"] = [str(c) for c in data.get("certifications", [])]
            result["education"] = [str(e) for e in data.get("education", [])]
        return result
    
    @staticmethod
    def parse_quiz(data: Any) -> list[dict]:
        """Parses a quiz generation response."""
        questions = []
        if isinstance(data, dict) and "questions" in data:
            raw_q = data["questions"]
        elif isinstance(data, list):
            raw_q = data
        else:
            return []
            
        for q in raw_q:
            if isinstance(q, dict) and "question" in q and "options" in q and "correct_index" in q:
                questions.append({
                    "question": str(q["question"]),
                    "options": [str(o) for o in q["options"]],
                    "correct_index": int(q["correct_index"]),
                    "explanation": str(q.get("explanation", ""))
                })
        return questions
