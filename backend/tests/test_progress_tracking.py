import os
import sys
import datetime as dt

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.session import Base
import models.sqlalchemy_models  # noqa: F401  (register models on Base)
from repositories import repositories as repos_module


@pytest.fixture
def test_db(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    monkeypatch.setattr(repos_module, "SessionLocal", session)
    yield session(autocommit=False)
    Base.metadata.drop_all(engine)


class TestStudyLogRepository:
    def test_upsert_creates_then_accumulates(self, test_db):
        user_id = "00000000-0000-0000-0000-000000000001"
        log_date = dt.date(2026, 9, 7)

        repo = repos_module.StudyLogRepository()
        first = repo.upsert(user_id, log_date, 2, "nmap")
        assert first.hours == 2

        second = repo.upsert(user_id, log_date, 3, "updated")
        assert second.hours == 5
        assert second.notes == "updated"

    def test_get_for_week_filters_dates(self, test_db):
        user_id = "00000000-0000-0000-0000-000000000001"
        repo = repos_module.StudyLogRepository()
        repo.upsert(user_id, dt.date(2026, 9, 8), 1)
        repo.upsert(user_id, dt.date(2026, 10, 1), 9)

        week_start = dt.date(2026, 9, 7)
        week_end = dt.date(2026, 9, 13)
        logs = repo.get_for_week(user_id, week_start, week_end)
        assert len(logs) == 1
        assert logs[0].hours == 1

    def test_get_all_for_user_limited(self, test_db):
        user_id = "00000000-0000-0000-0000-000000000001"
        repo = repos_module.StudyLogRepository()
        for i in range(5):
            repo.upsert(user_id, dt.date(2026, 9, 1 + i), 1)
        logs = repo.get_all_for_user(user_id, limit=3)
        assert len(logs) == 3


class TestWeeklyGoalRepository:
    def test_upsert_and_read(self, test_db):
        user_id = "00000000-0000-0000-0000-000000000001"
        week_start = dt.date(2026, 9, 7)

        repo = repos_module.WeeklyGoalRepository()
        goal = repo.upsert(user_id, week_start, 15)
        assert goal.goal_hours == 15

        fetched = repo.get_for_week(user_id, week_start)
        assert fetched is not None
        assert fetched.goal_hours == 15

        updated = repo.upsert(user_id, week_start, 20)
        assert updated.goal_hours == 20
        assert repo.get_for_week(user_id, week_start).goal_hours == 20

    def test_get_for_week_missing(self, test_db):
        user_id = "00000000-0000-0000-0000-000000000001"
        repo = repos_module.WeeklyGoalRepository()
        assert repo.get_for_week(user_id, dt.date(2026, 9, 7)) is None