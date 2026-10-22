"""Module 6: read-only student data access. student_id must come from the verified token."""
import sqlite3, pathlib
from contextlib import closing
from datetime import datetime

DB_PATH = "data/students.db"


def _conn():
    uri = pathlib.Path(DB_PATH).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def get_my_schedule(student_id: int):
    now = datetime.now().isoformat(timespec="minutes")
    with closing(_conn()) as con:
        return con.execute(
            "SELECT title, starts_at FROM live_classes "
            "WHERE student_id = ? AND starts_at >= ? ORDER BY starts_at LIMIT 3",
            (student_id, now)).fetchall()
