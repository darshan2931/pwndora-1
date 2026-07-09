#!/usr/bin/env python3
"""Generate API documentation from OpenAPI schema."""

import json
import requests


def generate():
    resp = requests.get("http://localhost:8000/openapi.json")
    schema = resp.json()
    with open("docs/api_reference.json", "w") as f:
        json.dump(schema, f, indent=2)
    print("API docs generated.")


if __name__ == "__main__":
    generate()
