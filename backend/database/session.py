import os
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cyberpath.db")

_connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=not DATABASE_URL.startswith("sqlite"),
    connect_args=_connect_args,
)

if not DATABASE_URL.startswith("sqlite"):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to PostgreSQL at %s", DATABASE_URL.split("@")[-1])
    except Exception as e:
        logger.warning("PostgreSQL unavailable (%s). Falling back to local SQLite.", e)
        sqlite_url = "sqlite:///./cyberpath.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        DATABASE_URL = sqlite_url

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
