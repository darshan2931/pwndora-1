import re
from typing import Optional


def sanitize_string(value: str, max_length: int = 1000) -> str:
    if not value:
        return ""
    value = value.strip()
    if len(value) > max_length:
        value = value[:max_length]
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"javascript:", "", value, flags=re.IGNORECASE)
    value = re.sub(r"on\w+\s*=", "", value, flags=re.IGNORECASE)
    return value


def sanitize_filename(filename: str) -> str:
    if not filename:
        return "upload"
    filename = re.sub(r"[^\w\-_\. ]", "_", filename)
    filename = re.sub(r"_+", "_", filename)
    return filename[:255]


def validate_skills_list(skills: list[str], max_skills: int = 50) -> list[str]:
    cleaned = []
    for skill in skills:
        if not isinstance(skill, str):
            continue
        skill = skill.strip()
        if not skill or len(skill) > 100:
            continue
        skill = re.sub(r"<[^>]+>", "", skill)
        if skill and skill not in cleaned:
            cleaned.append(skill)
        if len(cleaned) >= max_skills:
            break
    return cleaned


def validate_career_goal(goal: str) -> Optional[str]:
    goal = sanitize_string(goal, max_length=100)
    VALID_CAREERS = {
        "soc analyst", "penetration tester", "cloud security engineer",
        "application security engineer", "digital forensics analyst",
        "threat intelligence analyst",
    }
    if goal.lower() in VALID_CAREERS:
        return goal
    return None


def validate_study_hours(hours: int) -> int:
    if not isinstance(hours, int):
        return 10
    return max(1, min(hours, 40))
