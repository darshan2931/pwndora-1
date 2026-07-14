import os
import re
from typing import List
from app.domain.models import UserProfile, Skill
from knowledge.loader import knowledge_loader
from services.service_interfaces import ResumeService as IResumeService

class ResumeService(IResumeService):
    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.kb = knowledge_loader

    def parse(self, file_path: str) -> UserProfile:
        text = self._extract_text(file_path)
        skills = self.extract_skills(text)
        certs = self._detect_certifications(text)
        return UserProfile(skills=skills, certifications=certs)

    def _extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(file_path)
                if text:
                    return text
            except Exception:
                pass
        elif ext == ".docx":
            try:
                import docx
                doc = docx.Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs])
            except Exception:
                pass
        
        # Fallback to reading as text
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

    def extract_skills(self, text: str) -> List[Skill]:
        if not text:
            return []
        
        text_lower = text.lower()
        extracted_names = []
        
        # 1. Rule-based keyword matching against knowledge base
        skills_data = self.kb.get_skills()
        for skill in skills_data:
            name = skill["name"]
            pattern = rf"\b{re.escape(name.lower())}\b"
            if re.search(pattern, text_lower):
                extracted_names.append(name)
                
        # 2. AI enrichment / fallback if few skills are found and AI service is available
        if len(extracted_names) < 3 and self.ai_service:
            try:
                import asyncio
                from concurrent.futures import ThreadPoolExecutor
                
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        lambda: asyncio.run(self.ai_service.extract_skills_from_resume(text))
                    )
                    ai_result = future.result()
                    
                ai_skills = ai_result.get("skills", [])
                for s in ai_skills:
                    if s not in extracted_names:
                        match = self.kb.get_skill(s)
                        if match:
                            extracted_names.append(match["name"])
            except Exception:
                pass
                
        # Map names to Skill objects
        skills = []
        for name in extracted_names:
            skill_data = self.kb.get_skill(name) or {"name": name, "category": "Other", "difficulty": "intermediate"}
            skills.append(Skill(**skill_data))
        return skills

    def _detect_certifications(self, text: str) -> List[str]:
        if not text:
            return []
        text_lower = text.lower()
        extracted_certs = []
        
        certs_data = self.kb.get_certifications()
        for cert in certs_data:
            name = cert["name"]
            escaped = re.escape(name.lower())
            pattern = rf"(?<!\w){escaped}(?!\w)"
            if re.search(pattern, text_lower):
                extracted_certs.append(name)
        return extracted_certs
