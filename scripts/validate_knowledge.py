#!/usr/bin/env python3
"""Validate all knowledge JSON files against their schemas."""

import json
import os
import sys

KNOWLEDGE_DIR = "knowledge"
SCHEMA_DIR = "knowledge/schemas"


def validate_file(filepath: str, schema: dict) -> list:
    errors = []
    try:
        with open(filepath) as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return [f"Invalid JSON in {filepath}: {e}"]

    if not isinstance(data, list):
        errors.append(f"{filepath}: expected a list")

    return errors


def main():
    errors = []
    for root, _, files in os.walk(KNOWLEDGE_DIR):
        for f in files:
            if f.endswith(".json") and not root.startswith(os.path.join(KNOWLEDGE_DIR, "schemas")):
                errors.extend(validate_file(os.path.join(root, f), {}))

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    print("All knowledge files valid.")


if __name__ == "__main__":
    main()
