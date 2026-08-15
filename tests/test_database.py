try:
    import pytest
except ImportError:
    class pytest:
        @staticmethod
        def fixture(func):
            return func

import sqlite3
from unittest.mock import patch
from src.database import (
    save_job,
    get_all_applications,
    get_user_profile,
    save_user_profile
)

class MockConnection:
    def __init__(self, conn):
        self.conn = conn
    def cursor(self):
        return self.conn.cursor()
    def commit(self):
        return self.conn.commit()
    def close(self):
        pass


@pytest.fixture
def mock_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            job_id TEXT PRIMARY KEY,
            job_title TEXT NOT NULL,
            employer_name TEXT NOT NULL,
            job_city TEXT,
            job_apply_link TEXT,
            status TEXT NOT NULL,
            job_description TEXT,
            date_added TEXT,
            date_updated TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY DEFAULT 1,
            name TEXT,
            email TEXT,
            phone TEXT,
            preferred_role TEXT,
            preferred_location TEXT,
            remote_preference TEXT,
            experience_level TEXT,
            notice_period TEXT,
            skills TEXT,
            preferred_salary TEXT,
            education TEXT,
            CHECK (id = 1)
        )
    """)
    conn.commit()
    mock_conn = MockConnection(conn)
    yield mock_conn
    conn.close()


def test_save_and_retrieve_job(mock_db):
    with patch("src.database.get_connection", return_value=mock_db):
        res = save_job(
            "test_id",
            "Software Engineer",
            "Test Company",
            "San Francisco",
            "http://test.com",
            "Saved",
            "Test Description"
        )
        assert res is True

        apps = get_all_applications()
        assert len(apps) == 1
        assert apps[0]["job_title"] == "Software Engineer"
        assert apps[0]["job_description"] == "Test Description"


def test_save_and_retrieve_profile(mock_db):
    with patch("src.database.get_connection", return_value=mock_db):
        profile = {
            "name": "Sonia",
            "email": "sonia@example.com",
            "phone": "1234567890",
            "preferred_role": "Backend Engineer",
            "preferred_location": "Remote",
            "remote_preference": "Remote Only",
            "experience_level": "Mid",
            "notice_period": "30 days",
            "skills": "python, fastapi, postgresql",
            "preferred_salary": "15 LPA",
            "education": "B.Tech CSE"
        }
        res = save_user_profile(profile)
        assert res is True

        saved = get_user_profile()
        assert saved["name"] == "Sonia"
        assert saved["notice_period"] == "30 days"
        assert saved["email"] == "sonia@example.com"
