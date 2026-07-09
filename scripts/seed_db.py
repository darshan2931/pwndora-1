#!/usr/bin/env python3
"""Seed the database with demo data for presentations."""

import json
import sys


def load_knowledge(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def seed_assessments():
    pass


def seed_roadmaps():
    pass


if __name__ == "__main__":
    seed_assessments()
    seed_roadmaps()
    print("Database seeded.")
