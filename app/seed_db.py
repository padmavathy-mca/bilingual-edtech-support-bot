"""Create a fake student database for the demo."""
import sqlite3, pathlib
from datetime import datetime, timedelta


def seed(path="data/students.db"):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.executescript("""
        DROP TABLE IF EXISTS live_classes;
        DROP TABLE IF EXISTS students;
        CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, email TEXT);
        CREATE TABLE live_classes (id INTEGER PRIMARY KEY, student_id INTEGER,title TEXT, starts_at TEXT);""")
    con.executemany("INSERT INTO students VALUES (?,?,?)", [
        (1, "Student One", "s1@example.com"), (2, "Student Two", "s2@example.com"),
        (3, "Student Three", "s3@example.com")])
    now = datetime.now()

    def at(days, hour):
        return (now + timedelta(days=days)).replace(hour=hour, minute=0, second=0,
                microsecond=0).isoformat(timespec="minutes")
    con.executemany("INSERT INTO live_classes (student_id,title,starts_at) VALUES (?,?,?)", [
        (1, "Python Basics", at(1, 18)), (1, "SQL Workshop", at(3, 19)),
        (2, "Data Science Intro", at(2, 17)), (2, "Statistics Lab", at(4, 18)),
        (3, "Web Development", at(1, 20))])
    con.commit(); con.close()


if __name__ == "__main__":
    seed(); print("students.db created")
