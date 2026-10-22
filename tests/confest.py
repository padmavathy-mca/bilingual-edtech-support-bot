import pytest
from app import student_tools
from app.seed_db import seed


@pytest.fixture(autouse=True, scope="session")
def test_db(tmp_path_factory):
    path = str(tmp_path_factory.mktemp("db") / "students_test.db")
    seed(path)
    old = student_tools.DB_PATH
    student_tools.DB_PATH = path          # all tools now read the temp DB
    yield path
    student_tools.DB_PATH = old