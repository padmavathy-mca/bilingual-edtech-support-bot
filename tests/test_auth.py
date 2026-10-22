import jwt
import pytest
from app import auth


def test_valid_token_roundtrip():
    assert auth.verify_token(auth.create_token(2)) == 2

def test_tampered_token_rejected():
    bad = jwt.encode({"student_id": 2}, "wrong-secret", algorithm="HS256")
    with pytest.raises(Exception):
        auth.verify_token(bad)

def test_expired_token_rejected():
    with pytest.raises(Exception):
        auth.verify_token(auth.create_token(1, minutes=-1))

def test_unsigned_token_rejected():
    forged = jwt.encode({"student_id": 2}, None, algorithm="none")
    with pytest.raises(Exception):
        auth.verify_token(forged)
