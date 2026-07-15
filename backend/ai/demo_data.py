from typing import Any, overload, Literal

DEMO_RESPONSES: dict[str, Any] = {
    "resume_extraction": {
        "skills": ["Linux", "Python", "Networking", "TCP/IP"],
        "projects": ["Port Scanner", "Log Parser"],
        "certifications": ["CompTIA Security+"],
    },
    "mentor_responses": {
        "default": (
            "Based on your career assessment, I recommend focusing on building a strong "
            "foundation in networking and operating systems first. These skills are "
            "prerequisite to most cybersecurity roles. Start with hands-on labs using "
            "TryHackMe or Hack The Box to apply what you learn practically."
        ),
        "career_advice": (
            "For a career in cybersecurity, focus on these key areas:\n"
            "1. **Networking fundamentals** - Understanding TCP/IP, DNS, and HTTP is essential\n"
            "2. **Operating systems** - Get comfortable with both Linux and Windows\n"
            "3. **Security tools** - Learn industry-standard tools like Nmap, Wireshark, and SIEM platforms\n"
            "4. **Practical experience** - Build a home lab and practice with CTF challenges"
        ),
        "certification": (
            "For beginners, I recommend starting with CompTIA Security+ as it covers "
            "fundamental security concepts. After that, consider role-specific certifications "
            "like eJPT for penetration testing or Blue Team Level 1 for SOC analyst roles."
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
        if "cert" in question:
            return DEMO_RESPONSES["mentor_responses"]["certification"]
        elif "career" in question or "advice" in question:
            return DEMO_RESPONSES["mentor_responses"]["career_advice"]
        return DEMO_RESPONSES["mentor_responses"]["default"]
    elif prompt_type == "roadmap":
        return DEMO_RESPONSES["roadmap_explanation"]
    elif prompt_type == "career":
        return DEMO_RESPONSES["career_explanation"]
    elif prompt_type == "resume":
        return DEMO_RESPONSES["resume_extraction"]
    return DEMO_RESPONSES["mentor_responses"]["default"]
