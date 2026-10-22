import sqlite3
import pytest
from app.seed_db import seed
from app import student_tools


@pytest.fixture(autouse=True, scope="module")
def db():
    seed()


def titles(sid):
    return {t for t, _ in student_tools.get_my_schedule(sid)}


def test_students_see_only_their_own_classes():
    assert titles(1) == {"Python Basics", "SQL Workshop"}
    assert titles(2) == {"Data Science Intro", "Statistics Lab"}
    assert titles(1).isdisjoint(titles(2))


def test_unknown_student_gets_nothing():
    assert titles(999) == set()


def test_db_is_read_only():
    con = student_tools._conn()
    try:
        with pytest.raises(sqlite3.OperationalError):
            con.execute("DELETE FROM live_classes")
    finally:
        con.close()


def test_sql_injection_value_is_harmless():
    assert student_tools.get_my_schedule("1 OR 1=1") == []
