import logging
import json
from typing import Optional

from schemas.resume_profile import (
    ResumeProfileData,
    ExtractedURLs,
    ExtractedSkill,
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
)
from services.resume_text_extractor import ResumeTextExtractor, TextExtractionResult
from services.resume_url_extractor import ResumeURLExtractor
from app.ai.response_validator import ResponseValidator

logger = logging.getLogger(__name__)


class ResumeProfileService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service

    async def analyze(self, file_path: str) -> dict:
        extraction = ResumeTextExtractor.extract(file_path)
        urls = ResumeURLExtractor.extract(extraction.text)
        profile = await self._extract_profile_with_ai(extraction.text)

        return {
            "profile": profile,
            "urls": urls,
            "metadata": {
                "file_type": extraction.file_type,
                "character_count": extraction.character_count,
                "page_count": extraction.page_count,
            },
        }

    async def _extract_profile_with_ai(self, text: str) -> Optional[ResumeProfileData]:
        if not self.ai_service:
            logger.warning("No AI service available for resume profile extraction")
            return None

        try:
            prompt = f"Extract the following resume into a structured profile:\n\n{text}"

            raw_json = await self.ai_service.orchestrator.execute_task(
                task_prompt=prompt,
                template_name="resume_profile",
                json_mode=True,
            )

            if raw_json is None:
                logger.error("AI returned None for resume profile extraction")
                return None

            profile = self._validate_and_parse(raw_json)
            return profile

        except Exception as e:
            logger.error("AI profile extraction failed: %s", e)
            return None

    def _validate_and_parse(self, raw_data: dict) -> Optional[ResumeProfileData]:
        try:
            data = self._sanitize(raw_data)
            profile = ResumeProfileData(**data)
            return profile
        except Exception as e:
            logger.warning("Primary validation failed: %s. Attempting repair.", e)
            repaired = self._attempt_repair(raw_data)
            if repaired:
                try:
                    profile = ResumeProfileData(**repaired)
                    return profile
                except Exception as e2:
                    logger.error("Repaired data still invalid: %s", e2)
            return None

    def _sanitize(self, data: dict) -> dict:
        if not isinstance(data, dict):
            return {}

        if "skills" in data:
            cleaned_skills = []
            for s in data["skills"]:
                if isinstance(s, str):
                    cleaned_skills.append({"name": s, "category": None, "source": "resume"})
                elif isinstance(s, dict):
                    cleaned_skills.append({
                        "name": str(s.get("name", "")),
                        "category": s.get("category"),
                        "source": s.get("source", "resume"),
                    })
            data["skills"] = cleaned_skills

        if "experience" in data:
            for exp in data["experience"]:
                if isinstance(exp, dict):
                    if "technologies" not in exp:
                        exp["technologies"] = []

        if "projects" in data:
            for proj in data["projects"]:
                if isinstance(proj, dict):
                    if "technologies" not in proj:
                        proj["technologies"] = []

        if "education" not in data:
            data["education"] = []
        if "experience" not in data:
            data["experience"] = []
        if "skills" not in data:
            data["skills"] = []
        if "projects" not in data:
            data["projects"] = []
        if "certifications" not in data:
            data["certifications"] = []
        if "urls" not in data:
            data["urls"] = {"github": [], "linkedin": [], "portfolio": [], "personal_website": [], "other": []}

        return data

    def _attempt_repair(self, data: dict) -> Optional[dict]:
        try:
            repaired = {}

            repaired["full_name"] = str(data.get("full_name")) if data.get("full_name") else None
            repaired["email"] = str(data.get("email")) if data.get("email") else None
            repaired["phone"] = str(data.get("phone")) if data.get("phone") else None
            repaired["location"] = str(data.get("location")) if data.get("location") else None
            repaired["summary"] = str(data.get("summary")) if data.get("summary") else None

            repaired["education"] = []
            for e in (data.get("education") or []):
                if isinstance(e, dict):
                    repaired["education"].append({
                        "institution": str(e.get("institution")) if e.get("institution") else None,
                        "degree": str(e.get("degree")) if e.get("degree") else None,
                        "field": str(e.get("field")) if e.get("field") else None,
                        "start_date": str(e.get("start_date")) if e.get("start_date") else None,
                        "end_date": str(e.get("end_date")) if e.get("end_date") else None,
                    })

            repaired["experience"] = []
            for e in (data.get("experience") or []):
                if isinstance(e, dict):
                    repaired["experience"].append({
                        "company": str(e.get("company")) if e.get("company") else None,
                        "role": str(e.get("role")) if e.get("role") else None,
                        "description": str(e.get("description")) if e.get("description") else None,
                        "start_date": str(e.get("start_date")) if e.get("start_date") else None,
                        "end_date": str(e.get("end_date")) if e.get("end_date") else None,
                        "technologies": [str(t) for t in (e.get("technologies") or [])],
                    })

            repaired["skills"] = []
            for s in (data.get("skills") or []):
                if isinstance(s, str):
                    repaired["skills"].append({"name": s, "category": None, "source": "resume"})
                elif isinstance(s, dict):
                    repaired["skills"].append({
                        "name": str(s.get("name", "")),
                        "category": str(s.get("category")) if s.get("category") else None,
                        "source": str(s.get("source", "resume")),
                    })

            repaired["projects"] = []
            for p in (data.get("projects") or []):
                if isinstance(p, str):
                    repaired["projects"].append({"name": p, "description": None, "technologies": [], "url": None})
                elif isinstance(p, dict):
                    repaired["projects"].append({
                        "name": str(p.get("name")) if p.get("name") else None,
                        "description": str(p.get("description")) if p.get("description") else None,
                        "technologies": [str(t) for t in (p.get("technologies") or [])],
                        "url": str(p.get("url")) if p.get("url") else None,
                    })

            repaired["certifications"] = []
            for c in (data.get("certifications") or []):
                if isinstance(c, str):
                    repaired["certifications"].append({"name": c, "issuer": None, "date": None})
                elif isinstance(c, dict):
                    repaired["certifications"].append({
                        "name": str(c.get("name")) if c.get("name") else None,
                        "issuer": str(c.get("issuer")) if c.get("issuer") else None,
                        "date": str(c.get("date")) if c.get("date") else None,
                    })

            urls = data.get("urls") or {}
            repaired["urls"] = {}
            for key in ("github", "linkedin", "portfolio", "personal_website", "other"):
                val = urls.get(key, [])
                if isinstance(val, list):
                    repaired["urls"][key] = [str(u) for u in val]
                else:
                    repaired["urls"][key] = []

            return repaired

        except Exception as e:
            logger.error("Repair attempt failed: %s", e)
            return None
