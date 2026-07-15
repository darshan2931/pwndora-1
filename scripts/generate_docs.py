#!/usr/bin/env python3
"""Generate API documentation from OpenAPI schema."""

import json
import urllib.request


def generate():
    try:
        with urllib.request.urlopen("http://localhost:8000/openapi.json") as resp:
            schema = json.loads(resp.read().decode())
        with open("docs/api_reference.json", "w") as f:
            json.dump(schema, f, indent=2)
        print("API docs generated.")
    except Exception as e:
        print(f"Failed to generate API docs: {e}")


if __name__ == "__main__":
    generate()
