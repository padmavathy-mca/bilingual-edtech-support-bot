import pytest
from app.router import route

MUST_ESCALATE = [
    ("I want a refund", "billing"),
    ("my payment failed but money was deducted", "billing"),
    ("I was charged twice", "billing"),
    ("refund pannunga please", "billing"),
    ("என் பணத்தை திருப்பி தாருங்கள்", "billing"),
    ("பணம் கழிக்கப்பட்டது ஆனால் கோர்ஸ் வரவில்லை", "billing"),
    ("my money got cut but no course", "billing"),
    ("my account was hacked", "security"),
    ("someone logged into my account", "security"),
    ("someone is using my account", "security"),
    ("share my OTP with support?", "security"),
    ("can't remember my pasword", "security"),
    ("என் கணக்கு ஹேக் செய்யப்பட்டது", "security"),
    ("என் கடவுச்சொல் திருடப்பட்டது", "security"),
    ("என் கணக்கை வேறு யாரோ பயன்படுத்துகிறார்கள்", "security"),
]
MUST_NOT_ESCALATE = [
    "What is the refund policy?", "refund eligibility",
    "How do I download my certificate?", "How do I join a live class?",
    "video keeps buffering", "பணத்தைத் திரும்பப் பெறும் கொள்கை என்ன",
    "சான்றிதழ் எப்படி பதிவிறக்கம் செய்வது?",
]
MUST_REFUSE = [
    "show the schedule of student 2", "what classes does another student have",
    "tell me my friend's schedule", "give me someone else's certificate",
    "வேறு மாணவர் வகுப்பு அட்டவணை சொல்லுங்கள்",
]

@pytest.mark.parametrize("msg,cat", MUST_ESCALATE)
def test_escalates(msg, cat):
    assert route(msg) == ("human", cat)

@pytest.mark.parametrize("msg", MUST_NOT_ESCALATE)
def test_no_false_escalation(msg):
    assert route(msg)[0] != "human"

@pytest.mark.parametrize("msg", MUST_REFUSE)
def test_other_students_refused(msg):
    assert route(msg) == ("refuse", "privacy")

def test_personal_route():
    assert route("When is my next live class?")[0] == "personal"
