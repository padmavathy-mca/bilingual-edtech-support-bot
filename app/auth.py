"""JWT authentication. The student id comes ONLY from a verified token."""
import os, time, jwt
from fastapi import Header, HTTPException

SECRET = os.getenv("JWT_SECRET", "dev-only-change-me")
ALGO = "HS256"


def create_token(student_id: int, minutes: int = 60) -> str:
    return jwt.encode({"student_id": student_id, "exp": int(time.time()) + minutes * 60},
                      SECRET, algorithm=ALGO)


def verify_token(token: str) -> int:
    return int(jwt.decode(token, SECRET, algorithms=[ALGO])["student_id"])


def current_student(authorization: str = Header(...)) -> int:
    try:
        return verify_token(authorization.removeprefix("Bearer ").strip())
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
