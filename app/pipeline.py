"""Module 7: the full decision pipeline.
language -> guardrail router -> (human | refuse | student tool | cache -> retrieval -> 3-zone decision)"""
import time
from app.language import detect_language
from app.router import route
from app.decision import decide
from app import student_tools
from app.tickets import create_ticket
from app.lexical import lexical_support

MAX_LEN = 500

T = {
    "en": {
        "handoff": "This needs our support team. I've created a ticket so you won't need to repeat yourself.",
        "security_note": " For your safety, never share your password or OTP with anyone.",
        "fallback": "I don't have that information in our help center. I'm connecting you to our support team.",
        "refuse": "Sorry, I can't share anyone else's information. I can help with your own account and with general questions.",
        "confirm": "I'm not fully sure, but this article may help. If it isn't what you meant, I can connect you to our support team:",
        "schedule": "Your upcoming live classes:",
        "no_classes": "You have no upcoming live classes.",
        "empty": "Please type your question.",
    },
    "ta": {
        "handoff": "இதற்கு எங்கள் ஆதரவுக் குழு உதவ வேண்டும். நீங்கள் மீண்டும் விவரங்களைச் சொல்லத் தேவையில்லாதவாறு ஒரு டிக்கெட் உருவாக்கியுள்ளேன்.",
        "security_note": " உங்கள் பாதுகாப்புக்காக, கடவுச்சொல் அல்லது OTP-ஐ யாரிடமும் பகிர வேண்டாம்.",
        "fallback": "இந்தத் தகவல் எங்கள் உதவி மையத்தில் இல்லை. உங்களை எங்கள் ஆதரவுக் குழுவுடன் இணைக்கிறேன்.",
        "refuse": "மன்னிக்கவும், மற்றவர்களின் தகவல்களை என்னால் பகிர முடியாது. உங்கள் சொந்தக் கணக்கு மற்றும் பொதுவான கேள்விகளுக்கு உதவுகிறேன்.",
        "confirm": "எனக்கு முழுமையாக உறுதியில்லை, ஆனால் இந்தக் கட்டுரை உதவக்கூடும். நீங்கள் கேட்டது இதுவல்ல என்றால், ஆதரவுக் குழுவுடன் இணைக்கிறேன்:",
        "schedule": "உங்கள் வரவிருக்கும் நேரலை வகுப்புகள்:",
        "no_classes": "வரவிருக்கும் நேரலை வகுப்புகள் எதுவும் இல்லை.",
        "empty": "உங்கள் கேள்வியை உள்ளிடவும்.",
    },
}


def _format_chunk(chunk_text: str) -> str:
    lines = chunk_text.split("\n")[1:]           # drop the article title line
    heading, body = lines[0].lstrip("# ").strip(), "\n".join(lines[1:]).strip()
    return f"**{heading}**\n{body}"


def answer(message: str, student_id: int, retriever, cache) -> dict:
    t0 = time.perf_counter()
    message = (message or "").strip()[:MAX_LEN]
    lang = detect_language(message)
    key = "ta" if lang == "ta" else "en"          # reply language (Tanglish -> English)
    msgs = T[key]

    def done(**kw):
        kw.setdefault("escalated", False)
        kw.update(lang=lang, latency_ms=round((time.perf_counter() - t0) * 1000, 1))
        return kw

    if not message:
        return done(reply=msgs["empty"], action="empty")

    action, category = route(message)

    if action == "human":
        ticket = create_ticket(student_id, category, message, key)
        note = msgs["security_note"] if category == "security" else ""
        return done(reply=msgs["handoff"] + note, action="human", escalated=True,
                    category=category, ticket_id=ticket["ticket_id"])

    if action == "refuse":
        return done(reply=msgs["refuse"], action="refuse", category=category)

    if action == "personal":                       # student_id comes from the token only
        rows = student_tools.get_my_schedule(student_id)
        if not rows:
            return done(reply=msgs["no_classes"], action="personal", source="student_db")
        lines = [f"- {t} ({s.replace('T', ' ')})" for t, s in rows]
        return done(reply=msgs["schedule"] + "\n" + "\n".join(lines),
                    action="personal", source="student_db")

    cached = cache.get(message, key)
    if cached:
        return done(**{**cached, "action": "answer", "cached": True})

    hits = retriever.search(message, k=3, lang=key)
    zone, best = decide(hits)

    if zone == "confirm" and not lexical_support(message, best["text"]):
        zone = "fallback"                    # similar topic, but no shared words
    
    if zone == "fallback":
        ticket = create_ticket(student_id, "no_answer", message, key)
        return done(reply=msgs["fallback"], action="fallback", escalated=True,
                    category="no_answer", ticket_id=ticket["ticket_id"])

    result = {"reply": _format_chunk(best["text"]), "source": best["source"],
            "score": round(best["score"], 3)}
    if zone == "confirm":                          # never cache uncertain answers
        result["reply"] = msgs["confirm"] + "\n\n" + result["reply"]
        return done(**result, action="confirm")

    cache.put(message, key, result)
    return done(**result, action="answer", cached=False)
