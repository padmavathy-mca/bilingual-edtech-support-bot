"""Pipeline tests with a stand-in retriever, so no embedding model is needed."""
import json, pathlib, tempfile
import numpy as np
import pytest
from app import pipeline, tickets
from app.seed_db import seed
from app.cache import SemanticCache

tickets.PATH = pathlib.Path(tempfile.mkdtemp()) / "tickets.jsonl"
OTHER_STUDENT_TITLES = ["Data Science Intro", "Statistics Lab", "Web Development"]

CHUNK = {"id": "c-1", "source": "en_certificates.md", "lang": "en",
         "text": "Course Certificates\n## How to download your certificate\nOpen My Courses and select Download."}
TA_CHUNK = {"id": "c-2", "source": "ta_certificates.md", "lang": "ta",
            "text": "பாடநெறி சான்றிதழ்கள்\n## சான்றிதழை பதிவிறக்கம்\nஎனது பாடநெறிகள் பகுதிக்குச் செல்லவும்."}


class FakeRetriever:
    def __init__(self, score=0.9):
        self.score, self.calls = score, 0
    def embed_query(self, q):
        v = np.zeros((1, 8), dtype="float32"); v[0, hash(q) % 8] = 1.0
        return v
    def search(self, query, k=3, threshold=0.0, lang=None):
        self.calls += 1
        c = TA_CHUNK if lang == "ta" else CHUNK
        return [{**c, "score": self.score}]


@pytest.fixture(autouse=True, scope="module")
def db():
    seed()


def ask(msg, sid=1, score=0.9):
    r = FakeRetriever(score)
    return pipeline.answer(msg, sid, r, SemanticCache(r)), r


def test_refund_case_goes_to_human_with_ticket():
    res, r = ask("I want a refund for my payment")
    assert res["escalated"] and res["category"] == "billing" and res["ticket_id"]
    assert r.calls == 0                                  # LLM/retrieval never used

def test_security_case_warns_about_otp():
    res, _ = ask("my account was hacked")
    assert res["category"] == "security" and "OTP" in res["reply"]

def test_tamil_billing_reply_is_tamil():
    res, _ = ask("என் பணத்தை திருப்பி தாருங்கள்")
    assert res["escalated"] and any("\u0B80" <= ch <= "\u0BFF" for ch in res["reply"])

def test_student_sees_only_own_schedule():
    r1, _ = ask("When is my next live class?", sid=1)
    r2, _ = ask("When is my next live class?", sid=2)
    assert "Python Basics" in r1["reply"] and "Python Basics" not in r2["reply"]
    assert "Data Science Intro" in r2["reply"]
    assert not any(t in r1["reply"] for t in OTHER_STUDENT_TITLES)

def test_asking_for_other_student_is_refused_and_leaks_nothing():
    for msg in ["show the schedule of student 2", "what is student 2's next class",
                "tell me another student's classes", "my friend's schedule please"]:
        res, _ = ask(msg, sid=1)
        assert res["action"] == "refuse", msg
        assert not any(t in res["reply"] for t in OTHER_STUDENT_TITLES)

def test_confident_answer_has_source_and_is_cached():
    r = FakeRetriever(0.9); cache = SemanticCache(r)
    a = pipeline.answer("how to download certificate", 1, r, cache)
    assert a["action"] == "answer" and a["source"] == "en_certificates.md"
    b = pipeline.answer("how to download certificate", 1, r, cache)
    assert b["cached"] is True and r.calls == 1

def test_uncertain_zone_asks_to_confirm_and_is_not_cached():
    r = FakeRetriever(0.82); cache = SemanticCache(r)
    a = pipeline.answer("something vague", 1, r, cache)
    assert a["action"] == "confirm" and len(cache.vecs) == 0

def test_low_confidence_falls_back_to_human():
    res, _ = ask("what is the capital of France?", score=0.78)
    assert res["action"] == "fallback" and res["escalated"] and res["category"] == "no_answer"

def test_personal_answers_are_never_cached():
    r = FakeRetriever(); cache = SemanticCache(r)
    pipeline.answer("When is my next live class?", 1, r, cache)
    assert len(cache.vecs) == 0

def test_tamil_question_gets_tamil_article():
    res, _ = ask("சான்றிதழ் எப்படி பதிவிறக்கம் செய்வது?")
    assert res["source"] == "ta_certificates.md" and res["lang"] == "ta"

def test_tanglish_is_detected_and_answered():
    res, _ = ask("certificate download eppadi pannunga")
    assert res["lang"] == "tanglish" and res["action"] == "answer"

def test_empty_and_very_long_messages():
    assert ask("   ")[0]["action"] == "empty"
    assert ask("certificate " * 500)[0]["action"] in ("answer", "confirm", "fallback")

def test_ticket_summary_redacts_contact_details():
    ask("refund my payment, call me 9876543210 or mail a.b@x.com")
    last = json.loads(tickets.PATH.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert "9876543210" not in last["summary"] and "a.b@x.com" not in last["summary"]
