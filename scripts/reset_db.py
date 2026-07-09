#!/usr/bin/env python3
"""Reset the database — drop and recreate all tables."""

from database.session import engine, Base


def reset():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database reset complete.")


if __name__ == "__main__":
    reset()
