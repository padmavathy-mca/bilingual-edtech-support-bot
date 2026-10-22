"""Human-handoff tickets (stored in a local JSONL file for the demo)."""
import json, pathlib, uuid
from datetime import datetime
from app.logging_utils import redact

PATH = pathlib.Path("data/tickets.jsonl")


def create_ticket(student_id: int, category: str, message: str, lang: str) -> dict:
    t = {"ticket_id": uuid.uuid4().hex[:8], "student_id": student_id, "category": category,
         "lang": lang, "summary": redact(message)[:300],
         "priority": "high" if category in ("billing", "security") else "normal",
         "created_at": datetime.now().isoformat(timespec="seconds")}
    PATH.parent.mkdir(exist_ok=True)
    with PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(t, ensure_ascii=False) + "\n")
    return t
