"""Module 8: FastAPI service."""
import os, pathlib, time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field

from app import ingest, seed_db
from app.auth import current_student, create_token
from app.logging_utils import get_logger
from app.pipeline import answer

log = get_logger()
STATE = {}
RATE_LIMIT, WINDOW = 20, 60            # 20 messages / 60 s / student
_calls = defaultdict(deque)


@asynccontextmanager
async def lifespan(app):
    from app.retriever import Retriever            # heavy import: load once at startup
    from app.cache import SemanticCache
    if not pathlib.Path("data/chunks.json").exists():
        ingest.build()
    if not pathlib.Path("data/students.db").exists():
        seed_db.seed()
    STATE["retriever"] = Retriever()
    STATE["cache"] = SemanticCache(STATE["retriever"])
    log.info("Ready: %d chunks", len(STATE["retriever"].chunks))
    yield


app = FastAPI(title="EdTech Support Assistant", lifespan=lifespan)


class Msg(BaseModel):
    message: str = Field(min_length=1, max_length=500)


def _rate_limit(student_id: int):
    q, now = _calls[student_id], time.time()
    while q and now - q[0] > WINDOW:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        raise HTTPException(429, "Too many messages. Please wait a minute.")
    q.append(now)


@app.get("/health")
def health():
    return {"status": "ok", "chunks": len(STATE["retriever"].chunks) if STATE else 0}


@app.post("/chat")
def chat(body: Msg, student_id: int = Depends(current_student)):
    _rate_limit(student_id)
    result = answer(body.message, student_id, STATE["retriever"], STATE["cache"])
    log.info("student=%s action=%s lang=%s latency=%sms", student_id, result["action"],
             result["lang"], result["latency_ms"])          # message text is NOT logged
    return result


@app.get("/stats")
def stats(student_id: int = Depends(current_student)):
    c = STATE["cache"]
    return {"cache_hits": c.hits, "cache_misses": c.misses, "cache_size": len(c.vecs)}


@app.post("/dev/token/{student_id}")
def dev_token(student_id: int):
    """DEMO ONLY: stands in for the real login system. Disable in production."""
    if os.getenv("ALLOW_DEV_TOKENS", "1") != "1":
        raise HTTPException(404)
    return {"token": create_token(student_id)}
