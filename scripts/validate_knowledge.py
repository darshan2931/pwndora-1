#!/usr/bin/env python3
"""Validate all knowledge JSON files against their schemas."""

import json
import os
import sys
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge" / "versions" / "v1" / "current"

VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
VALID_PROJECT_DIFFICULTIES = {"Easy", "Medium", "Hard"}
VALID_CATEGORIES = {
    "Operating Systems", "Networking", "Programming", "Web Security",
    "Cloud", "Defensive Security", "Offensive Security",
    "Digital Forensics", "Application Security", "DevOps",
}

REQUIRED_FIELDS = {
    "roles.json": ["role", "description", "required_skills"],
    "skills.json": ["name", "category", "difficulty"],
    "projects.json": ["title", "difficulty", "skills", "estimated_hours"],
    "certifications.json": ["name", "vendor", "difficulty", "recommended_for"],
    "learning_paths.json": ["career", "sequence"],
}


def load_json(filepath: Path) -> tuple[list | None, str | None]:
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return None, str(e)
    if not isinstance(data, list):
        return None, f"Expected a list, got {type(data).__name__}"
    return data, None


def validate_file(filepath: Path, filename: str) -> list[str]:
    errors = []
    required = REQUIRED_FIELDS.get(filename, [])

    data, load_err = load_json(filepath)
    if data is None:
        return [f"{filename}: {load_err or 'unknown load error'}"]

    for i, item in enumerate(data):
        for field in required:
            if field not in item:
                errors.append(f"{filename}[{i}]: missing required field '{field}'")

        if filename == "skills.json":
            diff = item.get("difficulty", "")
            if diff and diff not in VALID_DIFFICULTIES:
                errors.append(f"{filename}[{i}] '{item.get('name')}': invalid difficulty '{diff}'")
            cat = item.get("category", "")
            if cat and cat not in VALID_CATEGORIES:
                errors.append(f"{filename}[{i}] '{item.get('name')}': invalid category '{cat}'")
            if not isinstance(item.get("prerequisites", []), list):
                errors.append(f"{filename}[{i}] '{item.get('name')}': prerequisites must be a list")

        if filename == "projects.json":
            diff = item.get("difficulty", "")
            if diff and diff not in VALID_PROJECT_DIFFICULTIES:
                errors.append(f"{filename}[{i}] '{item.get('title')}': invalid difficulty '{diff}'")
            skills = item.get("skills", [])
            if not isinstance(skills, list):
                errors.append(f"{filename}[{i}] '{item.get('title')}': skills must be a list")

        if filename == "roles.json":
            for field in ["required_skills", "optional_skills", "recommended_certifications", "suggested_projects"]:
                if field in item and not isinstance(item[field], list):
                    errors.append(f"{filename}[{i}] '{item.get('role')}': {field} must be a list")

    return errors


def validate_references(data_dir: Path) -> list[str]:
    errors = []

    roles, _ = load_json(data_dir / "roles.json")
    skills, _ = load_json(data_dir / "skills.json")
    certs, _ = load_json(data_dir / "certifications.json")
    paths, _ = load_json(data_dir / "learning_paths.json")

    if not roles or not skills:
        return ["Cannot validate references: roles.json or skills.json missing"]

    skill_names = {s["name"].lower() for s in skills}
    role_names = {r["role"].lower() for r in roles}
    cert_names = {c["name"].lower() for c in certs} if certs else set()

    for i, role in enumerate(roles):
        for skill in role.get("required_skills", []) + role.get("optional_skills", []):
            if skill.lower() not in skill_names:
                errors.append(f"roles.json[{i}] '{role['role']}': references unknown skill '{skill}'")
        for cert in role.get("recommended_certifications", []):
            if cert.lower() not in cert_names:
                errors.append(f"roles.json[{i}] '{role['role']}': references unknown cert '{cert}'")

    for i, skill in enumerate(skills):
        for prereq in skill.get("prerequisites", []):
            if prereq.lower() not in skill_names:
                errors.append(f"skills.json[{i}] '{skill['name']}': references unknown prerequisite '{prereq}'")

    if paths:
        for i, path in enumerate(paths):
            if path.get("career", "").lower() not in role_names:
                errors.append(f"learning_paths.json[{i}]: references unknown career '{path.get('career')}'")
            for skill in path.get("sequence", []):
                if skill.lower() not in skill_names:
                    errors.append(f"learning_paths.json[{i}]: references unknown skill '{skill}'")

    return errors


def main():
    errors = []

    if not KNOWLEDGE_DIR.exists():
        print(f"ERROR: Knowledge directory not found: {KNOWLEDGE_DIR}")
        sys.exit(1)

    json_files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(".json")]
    if not json_files:
        print(f"ERROR: No JSON files found in {KNOWLEDGE_DIR}")
        sys.exit(1)

    for filename in sorted(json_files):
        filepath = KNOWLEDGE_DIR / filename
        file_errors = validate_file(filepath, filename)
        errors.extend(file_errors)

    ref_errors = validate_references(KNOWLEDGE_DIR)
    errors.extend(ref_errors)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):\n")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)

    print(f"All {len(json_files)} knowledge files validated successfully.")
    print(f"  Roles: {len(roles) if (roles := json.loads((KNOWLEDGE_DIR / 'roles.json').read_text())) else 0}")
    print(f"  Skills: {len(skills) if (skills := json.loads((KNOWLEDGE_DIR / 'skills.json').read_text())) else 0}")
    print(f"  Projects: {len(json.loads((KNOWLEDGE_DIR / 'projects.json').read_text()))}")
    print(f"  Certifications: {len(json.loads((KNOWLEDGE_DIR / 'certifications.json').read_text()))}")
    print(f"  Learning Paths: {len(json.loads((KNOWLEDGE_DIR / 'learning_paths.json').read_text()))}")


if __name__ == "__main__":
    main()
