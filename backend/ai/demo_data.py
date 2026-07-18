from typing import Any, overload, Literal

DEMO_RESPONSES: dict[str, Any] = {
    "resume_extraction": {
        "skills": ["Linux", "Python", "Networking", "TCP/IP"],
        "projects": ["Port Scanner", "Log Parser"],
        "certifications": ["CompTIA Security+"],
    },
    "mentor_responses": {
        "default": (
            "Based on your career assessment, here are my recommendations:\n\n"
            "1. **Focus on your missing skills first** — these are the biggest gaps "
            "between where you are and where you need to be.\n"
            "2. **Build hands-on experience** — use platforms like TryHackMe or "
            "Hack The Box to practice the skills you're learning.\n"
            "3. **Follow the learning path order** — each skill builds on the "
            "previous one, so don't skip ahead.\n\n"
            "Would you like me to go deeper into any specific area?"
        ),
        "career_advice": (
            "Here's a structured approach to breaking into cybersecurity:\n\n"
            "**1. Strengthen your foundation**\n"
            "Make sure your networking and OS fundamentals are solid. These are "
            "prerequisites for every security role.\n\n"
            "**2. Get hands-on early**\n"
            "Don't just read — build a home lab, run security tools, and practice "
            "with CTF challenges. Employers value practical experience.\n\n"
            "**3. Pursue the right certifications**\n"
            "Start with entry-level certs like CompTIA Security+, then move to "
            "role-specific ones as you specialize.\n\n"
            "**4. Build a portfolio**\n"
            "Document your projects on GitHub. Write blog posts about what you learn. "
            "This sets you apart from other candidates."
        ),
        "certification": (
            "Here's how to think about certifications:\n\n"
            "**Entry-level (start here):**\n"
            "- CompTIA Security+ — industry standard, covers fundamentals\n"
            "- Google Cybersecurity Professional Certificate — great for beginners\n\n"
            "**Intermediate (after 1-2 years):**\n"
            "- Blue Team Level 1 — for SOC/defensive roles\n"
            "- eJPT — for penetration testing\n"
            "- CCSK — for cloud security\n\n"
            "**Advanced (specialize):**\n"
            "- OSCP — gold standard for pen testing\n"
            "- CISSP — for management/architect roles\n"
            "- GCFA — for forensics\n\n"
            "Don't collect certs blindly — choose ones that align with your target role."
        ),
        "skills": (
            "The most in-demand cybersecurity skills right now:\n\n"
            "**Technical:**\n"
            "- SIEM (Splunk, Sentinel) — every SOC needs this\n"
            "- Cloud security (AWS/Azure) — most infra is moving to cloud\n"
            "- Python/automation — scripting saves hours of manual work\n"
            "- Container security (Docker, Kubernetes) — critical for DevSecOps\n\n"
            "**Soft skills:**\n"
            "- Communication — you'll need to explain threats to non-technical people\n"
            "- Analytical thinking — connecting dots across logs and events\n"
            "- Documentation — writing clear incident reports\n\n"
            "Focus on 2-3 technical skills deeply rather than 10 superficially."
        ),
        "learning_path": (
            "Here's the optimal learning sequence for cybersecurity:\n\n"
            "**Phase 1 — Foundations (4-6 weeks):**\n"
            "Networking (TCP/IP, DNS, HTTP) → Linux basics → Windows basics\n\n"
            "**Phase 2 — Core Security (6-8 weeks):**\n"
            "Security concepts → SIEM fundamentals → Log analysis → Incident response basics\n\n"
            "**Phase 3 — Specialization (8-12 weeks):**\n"
            "Choose your path: offensive (Nmap, Burp Suite, Metasploit) OR defensive "
            "(EDR, threat hunting, forensics)\n\n"
            "**Phase 4 — Portfolio Building (ongoing):**\n"
            "Build projects, document your work, contribute to security communities\n\n"
            "The key is not to rush — understanding beats speed."
        ),
        "transition": (
            "Transitioning into cybersecurity from another field? Here's my advice:\n\n"
            "**Leverage what you already know:**\n"
            "- IT background? Focus on security-specific skills\n"
            "- Development? Application security is a natural fit\n"
            "- Management? GRC and risk assessment use similar frameworks\n\n"
            "**Bridge the gaps:**\n"
            "1. Complete a foundational cert (Security+)\n"
            "2. Build a home lab and practice daily\n"
            "3. Join security communities (Discord, Reddit, local meetups)\n"
            "4. Volunteer for security tasks at your current job\n\n"
            "**Timeline:** Most transitions take 6-12 months of focused learning. "
            "Don't quit your job yet — build skills alongside it."
        ),
    },
    "roadmap_explanation": (
        "This learning roadmap is designed to build your skills progressively. "
        "Each step builds on the previous one, ensuring you have the necessary "
        "foundations before moving to advanced topics. The estimated duration "
        "is based on your available study hours per week."
    ),
    "career_explanation": (
        "Your current readiness score reflects the skills you already have compared "
        "to what's required for your target role. The missing skills are prioritized "
        "by importance and dependency. Focus on the top items first to maximize "
        "your career readiness."
    ),
}


@overload
def get_demo_response(prompt_type: Literal["resume"], **kwargs) -> dict[str, list[str]]: ...

@overload
def get_demo_response(prompt_type: Literal["mentor", "roadmap", "career"], **kwargs) -> str: ...

@overload
def get_demo_response(prompt_type: str, **kwargs) -> Any: ...

def get_demo_response(prompt_type: str, **kwargs) -> Any:
    if prompt_type == "mentor":
        question = kwargs.get("question", "").lower()
        if "cert" in question or "certification" in question:
            return DEMO_RESPONSES["mentor_responses"]["certification"]
        elif "career" in question or "advice" in question or "path" in question:
            return DEMO_RESPONSES["mentor_responses"]["career_advice"]
        elif "skill" in question or "learn" in question or "know" in question:
            return DEMO_RESPONSES["mentor_responses"]["skills"]
        elif "roadmap" in question or "sequence" in question or "order" in question or "step" in question:
            return DEMO_RESPONSES["mentor_responses"]["learning_path"]
        elif "transition" in question or "switch" in question or "change" in question or "from" in question:
            return DEMO_RESPONSES["mentor_responses"]["transition"]
        return DEMO_RESPONSES["mentor_responses"]["default"]
    elif prompt_type == "roadmap":
        return DEMO_RESPONSES["roadmap_explanation"]
    elif prompt_type == "career":
        return DEMO_RESPONSES["career_explanation"]
    elif prompt_type == "resume":
        return DEMO_RESPONSES["resume_extraction"]
    return DEMO_RESPONSES["mentor_responses"]["default"]
