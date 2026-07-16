import hashlib
import json
import logging
import re
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Optional

import httpx

from app.domain.models import Assessment, Roadmap
from ai.demo_data import get_demo_response

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"

MAX_RETRIES = 2
TIMEOUT_SECONDS = 30

CACHE_TTL = 300
MAX_CACHE_SIZE = 500

_response_cache: OrderedDict[str, tuple[str, float]] = OrderedDict()


def _cache_key(prefix: str, *args) -> str:
    raw = f"{prefix}:{':'.join(str(a) for a in args)}"
    return hashlib.md5(raw.encode()).hexdigest()


class AIClient:
    FALLBACK_MODELS = ["open-mistral-7b", "mistral-tiny"]

    def __init__(self, api_keys: list[str], model: str = "mistral-small-latest"):
        if not api_keys:
            raise ValueError("At least one API key must be provided")
        self.api_keys = api_keys
        self.current_key_idx = 0
        self.base_url = "https://api.mistral.ai/v1"
        self.model = model

    def _get_next_api_key(self) -> str:
        key = self.api_keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        return key

    async def chat(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        models_to_try = [self.model] + self.FALLBACK_MODELS
        last_error = None

        for model in models_to_try:
            for attempt in range(MAX_RETRIES + 1):
                try:
                    current_key = self._get_next_api_key()
                    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                        resp = await client.post(
                            f"{self.base_url}/chat/completions",
                            headers={
                                "Authorization": f"Bearer {current_key}",
                                "Content-Type": "application/json",
                            },
                            json={
                                "model": model,
                                "messages": messages,
                                "temperature": 0.7,
                                "max_tokens": 1024,
                            },
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
                    last_error = e
                    logger.warning(
                        "Mistral API call failed for model %s (attempt %d/%d): %s",
                        model,
                        attempt + 1,
                        MAX_RETRIES + 1,
                        e,
                    )
        raise RuntimeError(f"Mistral API failed for all models. Last error: {last_error}")

    async def chat_with_history(self, history: list[dict], system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)

        models_to_try = [self.model] + self.FALLBACK_MODELS
        last_error = None

        for model in models_to_try:
            for attempt in range(MAX_RETRIES + 1):
                try:
                    current_key = self._get_next_api_key()
                    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                        resp = await client.post(
                            f"{self.base_url}/chat/completions",
                            headers={
                                "Authorization": f"Bearer {current_key}",
                                "Content-Type": "application/json",
                            },
                            json={
                                "model": model,
                                "messages": messages,
                                "temperature": 0.7,
                                "max_tokens": 1024,
                            },
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
                    last_error = e
                    logger.warning(
                        "Mistral API call failed for model %s (attempt %d/%d): %s",
                        model,
                        attempt + 1,
                        MAX_RETRIES + 1,
                        e,
                    )
        raise RuntimeError(f"Mistral API failed for all models. Last error: {last_error}")


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    return path.read_text().strip()


class PromptBuilder:
    def build_resume_extraction(self, resume_text: str) -> tuple[str, str]:
        system = _load_prompt("resume")
        prompt = (
            "Extract cybersecurity skills, certifications, tools, and projects "
            "from the following resume text.\n\n"
            f"Resume:\n{resume_text}"
        )
        return system, prompt

    def build_roadmap_explanation(self, assessment: Assessment, roadmap: Roadmap) -> tuple[str, str]:
        system = _load_prompt("roadmap")
        prompt = (
            f"Target Role: {assessment.target_career.title}\n"
            f"Readiness Score: {assessment.readiness_score}%\n"
            f"Matched Skills: {[s.name for s in assessment.matched_skills]}\n"
            f"Missing Skills: {[s.name for s in assessment.missing_skills]}\n"
            f"Roadmap Steps: {[step.skill.name for step in roadmap.steps]}\n"
            f"Estimated Duration: {roadmap.estimated_weeks} weeks"
        )
        return system, prompt

    def build_career_explanation(self, assessment: Assessment) -> tuple[str, str]:
        system = _load_prompt("career_explainer")
        prompt = (
            f"Career: {assessment.target_career.title}\n"
            f"Readiness: {assessment.readiness_score}%\n"
            f"Matched: {[s.name for s in assessment.matched_skills]}\n"
            f"Missing: {[s.name for s in assessment.missing_skills]}"
        )
        return system, prompt

    def build_mentor_prompt(self, assessment: Assessment, question: str) -> tuple[str, str]:
        system = _load_prompt("mentor")
        prompt = (
            f"User Profile:\n"
            f"- Target Role: {assessment.target_career.title}\n"
            f"- Readiness: {assessment.readiness_score}%\n"
            f"- Known Skills: {[s.name for s in assessment.matched_skills]}\n"
            f"- Missing Skills: {[s.name for s in assessment.missing_skills]}\n\n"
            f"Question: {question}"
        )
        return system, prompt

    def build_resume_review(self, resume_text: str, career_goal: str) -> tuple[str, str]:
        system = _load_prompt("resume_reviewer")
        prompt = (
            f"Career Goal: {career_goal}\n\n"
            f"Resume:\n{resume_text}"
        )
        return system, prompt


class ResponseValidator:
    KNOWN_SKILL_PATTERNS = [
        "linux", "windows", "python", "javascript", "bash", "powershell",
        "nmap", "burp suite", "owasp", "siem", "splunk", "aws", "azure",
        "docker", "kubernetes", "metasploit", "active directory", "mitre att&ck",
        "volatility", "autopsy", "sql", "tcp/ip", "dns", "http", "firewalls",
        "edr", "sast", "dast", "ci/cd", "terraform", "vpn",
    ]

    @staticmethod
    def validate_json(text: str) -> Optional[dict]:
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
            return json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            return None

    @staticmethod
    def validate_no_hallucinations(text: str, known_skills: list[str]) -> bool:
        if not text:
            return True
        text_lower = text.lower()

        # Load all skills and certifications from knowledge base
        from knowledge.loader import knowledge_loader
        all_skills = [s["name"].lower() for s in knowledge_loader.get_skills()]
        all_certs = [c["name"].lower() for c in knowledge_loader.get_certifications()]
        all_taxonomy = list(set(all_skills + all_certs))

        # Check for matching taxonomy items
        allowed_lower = [k.lower() for k in known_skills]

        for item in all_taxonomy:
            pattern = rf"\b{re.escape(item)}\b"
            if re.search(pattern, text_lower):
                if item not in allowed_lower:
                    if item in ["go"] and not re.search(r"\bgo\b (?:programming|language)", text_lower):
                        continue
                    logger.warning("Hallucination detected: skill/cert '%s' mentioned but not in allowed context.", item)
                    return False

        # Additional whitelist validation for non-taxonomy words
        all_known = [s.lower() for s in ResponseValidator.KNOWN_SKILL_PATTERNS + known_skills]
        all_known_unique = list(set(all_known))

        words = re.findall(r"\b[a-z]{3,}\b", text_lower)
        for word in words:
            if word not in all_known_unique and word not in {
                "you", "the", "and", "for", "are", "but", "not", "your", "this",
                "that", "with", "can", "has", "have", "will", "should", "need",
                "learn", "skills", "role", "focus", "based", "on", "from", "all",
                "well", "also", "some", "more", "most", "best", "key", "way",
                "get", "start", "build", "understand", "using", "practice",
                "recommend", "consider", "after", "first", "next", "then",
                "make", "sure", "keep", "work", "try", "help", "like",
                "important", "foundation", "essential", "concepts", "security",
                "cybersecurity", "career", "readiness", "score", "target", "already",
                "know", "missing", "areas", "tools", "framework", "learning", "roadmap",
                "incident", "response", "threats", "monitoring", "analysis", "analyst",
                "engineer", "tester", "penetration", "cloud", "application", "forensics",
                "digital", "intelligence", "practice", "hands-on", "labs", "projects",
                "certifications", "certified", "professional", "certificate", "exam",
                "course", "study", "hours", "weekly", "timeline", "duration", "weeks",
                "months", "progress", "milestone", "step", "steps", "order", "sequence",
                "prerequisites", "builds", "builds-on", "leads", "helps", "prepare",
                "job-ready", "job", "market", "employers", "skills-gap", "gap", "close",
                "solid", "foundation", "strong", "basic", "fundamental", "fundamentals",
                "highly", "recommended", "highly-recommended", "start", "starting",
                "before", "moving", "advanced", "intermediate", "beginner", "easy",
                "medium", "hard", "difficulty", "estimated", "time", "hours", "days",
                "structured", "path", "guidance", "advisor", "mentor", "advice",
                "suggest", "suggestions"
            }:
                logger.warning("Unrecognized/hallucinated word detected: '%s'", word)
                return False
        return True

    @staticmethod
    def compute_confidence(text: str, known_skills: list[str], known_certs: Optional[list[str]] = None) -> float:
        if not text:
            return 0.0

        score = 0.5

        skill_mentions = sum(1 for s in known_skills if s.lower() in text.lower())
        if known_skills:
            skill_ratio = skill_mentions / len(known_skills)
            score += skill_ratio * 0.2

        if len(text) > 50:
            score += 0.1
        if len(text) > 200:
            score += 0.1

        if "based on" in text.lower() or "your profile" in text.lower():
            score += 0.1

        return min(1.0, round(score, 2))

    @staticmethod
    def extract_skills_from_json(data: Any) -> dict:
        result: dict[str, list[str]] = {"skills": [], "projects": [], "certifications": []}
        if isinstance(data, dict):
            result["skills"] = [
                s if isinstance(s, str) else str(s)
                for s in data.get("skills", [])
            ]
            result["projects"] = [
                p if isinstance(p, str) else str(p)
                for p in data.get("projects", [])
            ]
            result["certifications"] = [
                c if isinstance(c, str) else str(c)
                for c in data.get("certifications", [])
            ]
        return result


class AIService:
    MAX_SESSIONS = 100
    SESSION_TTL = 3600  # 1 hour

    def __init__(self, client: AIClient):
        self.client = client
        self.prompt_builder = PromptBuilder()
        self.validator = ResponseValidator()
        self._conversation_history: dict[str, tuple[list[dict], float]] = {}

    def _get_cache(self, key: str) -> Optional[str]:
        if key in _response_cache:
            value, ts = _response_cache[key]
            if time.time() - ts < CACHE_TTL:
                _response_cache.move_to_end(key)
                return value
            del _response_cache[key]
        return None

    def _set_cache(self, key: str, value: str):
        _response_cache[key] = (value, time.time())
        _response_cache.move_to_end(key)
        while len(_response_cache) > MAX_CACHE_SIZE:
            _response_cache.popitem(last=False)

    def _get_session(self, session_id: str) -> list[dict]:
        if session_id in self._conversation_history:
            history, ts = self._conversation_history[session_id]
            if time.time() - ts < self.SESSION_TTL:
                self._conversation_history[session_id] = (history, time.time())
                return history
            del self._conversation_history[session_id]
        return []

    def _save_session(self, session_id: str, history: list[dict]):
        self._conversation_history[session_id] = (history, time.time())
        while len(self._conversation_history) > self.MAX_SESSIONS:
            oldest = min(self._conversation_history, key=lambda k: self._conversation_history[k][1])
            del self._conversation_history[oldest]

    async def extract_skills_from_resume(self, resume_text: str) -> dict:
        ck = _cache_key("resume", resume_text[:200])
        cached = self._get_cache(ck)
        if cached:
            return json.loads(cached)

        try:
            system, prompt = self.prompt_builder.build_resume_extraction(resume_text)
            response = await self.client.chat(prompt, system)
            data = self.validator.validate_json(response)
            if data is None:
                logger.warning("AI returned invalid JSON, using demo data")
                return get_demo_response("resume")
            result = self.validator.extract_skills_from_json(data)
            self._set_cache(ck, json.dumps(result))
            return result
        except RuntimeError as e:
            logger.warning("AI unavailable, using demo data: %s", e)
            return get_demo_response("resume")

    async def explain_roadmap(self, assessment: Assessment, roadmap: Roadmap) -> tuple[str, float]:
        ck = _cache_key("roadmap", str(assessment.readiness_score), str(roadmap.estimated_weeks))
        cached = self._get_cache(ck)
        if cached:
            data = json.loads(cached)
            return data["text"], data["confidence"]

        try:
            system, prompt = self.prompt_builder.build_roadmap_explanation(assessment, roadmap)
            text = await self.client.chat(prompt, system)
            known = [s.name for s in assessment.matched_skills + assessment.missing_skills]
            confidence = self.validator.compute_confidence(text, known)
            self._set_cache(ck, json.dumps({"text": text, "confidence": confidence}))
            return text, confidence
        except RuntimeError as e:
            logger.warning("AI unavailable, using demo data: %s", e)
            text = get_demo_response("roadmap")
            return text, 0.5

    async def explain_career(self, assessment: Assessment) -> tuple[str, float]:
        ck = _cache_key("career", str(assessment.readiness_score), assessment.target_career.title)
        cached = self._get_cache(ck)
        if cached:
            data = json.loads(cached)
            return data["text"], data["confidence"]

        try:
            system, prompt = self.prompt_builder.build_career_explanation(assessment)
            text = await self.client.chat(prompt, system)
            known = [s.name for s in assessment.matched_skills + assessment.missing_skills]
            confidence = self.validator.compute_confidence(text, known)
            self._set_cache(ck, json.dumps({"text": text, "confidence": confidence}))
            return text, confidence
        except RuntimeError as e:
            logger.warning("AI unavailable, using demo data: %s", e)
            text = get_demo_response("career")
            return text, 0.5

    async def mentor_chat(self, assessment: Assessment, question: str, session_id: str = "default") -> str:
        system = _load_prompt("mentor")
        history = self._get_session(session_id)
        history.append({"role": "user", "content": question})

        context_prompt = (
            f"User Profile:\n"
            f"- Target Role: {assessment.target_career.title}\n"
            f"- Readiness: {assessment.readiness_score}%\n"
            f"- Known Skills: {[s.name for s in assessment.matched_skills]}\n"
            f"- Missing Skills: {[s.name for s in assessment.missing_skills]}\n\n"
            f"Question: {question}"
        )

        try:
            full_history = [{"role": "user", "content": context_prompt}] if len(history) <= 1 else history
            response = await self.client.chat_with_history(full_history, system)
            history.append({"role": "assistant", "content": response})
            if len(history) > 20:
                history = history[-20:]
            self._save_session(session_id, history)
            return response
        except RuntimeError as e:
            logger.warning("AI unavailable, using demo data: %s", e)
            return get_demo_response("mentor", question=question)

    async def review_resume(self, resume_text: str, career_goal: str) -> str:
        try:
            system, prompt = self.prompt_builder.build_resume_review(resume_text, career_goal)
            return await self.client.chat(prompt, system)
        except RuntimeError as e:
            logger.warning("AI unavailable, using demo data: %s", e)
            return "AI service is currently unavailable. Please try again later."

    def clear_session(self, session_id: str):
        self._conversation_history.pop(session_id, None)
