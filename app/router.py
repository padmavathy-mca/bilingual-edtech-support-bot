"""Module 4: guardrail router. Decides: human / refuse / personal / faq."""
import re
import unicodedata

SECURITY = [
    "phishing", "scam", "unknown login", "login alert", "login was used", "unauthori",
    "not safe", "பாதுகாப்பாக இல்லை", "அக்கவுண்ட்",
    "hacked", "hack", "otp", "password", "pasword", "passwrd", "unauthorized",
    "unauthorised", "stolen", "someone logged", "someone is using my account",
    "someone else is using", "suspicious", "compromised", "account misuse",
    "கடவுச்சொல்", "ஹேக்", "ஓடிபி", "திருடப்பட்ட", "அங்கீகரிக்கப்படாத",
    "வேறு யாரோ", "யாரோ என் கணக்கை",
]
BILLING = [
    "refund", "payment", "paid", "charged", "deducted", "invoice error", "money back",
    "double charge", "transaction", "debited", "money got cut", "amount cut",
    "money cut", "cut from my", "return my fee", "return my money", "amount", "debit",
    "give money", "thirumba", "கட்டணத்தை", "கட்டணம் திரும்ப", "திருப்பி கொடுங்கள்", "cancel my enrollment", "ரீஃபண்ட்", "பணம்", "பணத்", "திரும்பப் பெற",
    "பரிவர்த்தனை", "paisa", "panam", "kaasu",
]
POLICY_HINTS = ["policy", "in general", "methods", "accept", "how do refunds work", "how does a refund", "eligib", "terms", "how long does a refund", "how are refunds",
                "கொள்கை", "தகுதி", "விதிமுறை"]
CASE_HINTS = ["my ", "from my card", "taken twice", "i want", "i need", "i paid", "i was", "deducted", "twice", "double",
              "failed", "not received", "got cut", "pannunga", "vapas", "என் ", "எனக்கு",
              "எடுக்கப்பட்ட", "கழிக்கப்பட்ட", "தாருங்கள்"]

# Asking about somebody else's data -> refuse politely (privacy)
OTHER_PERSON = [
    r"\bstudent\s*#?\s*\d+", r"\banother (student|user|person)\b", r"\bother (student|user)s?\b",
    r"\bsomeone else'?s?\b", r"\b(his|her|their) (schedule|class|classes|certificate|account|marks)\b",
    r"\b(my )?(friend|brother|sister|classmate)'?s? (schedule|class|classes|certificate|account|marks)\b",
    r"வேறு (மாணவர்|ஒருவர்)", r"மற்றொரு மாணவர்", r"நண்பரின்",
]
PERSONAL = [
    r"\bmy\b.*\b(class|classes|schedule|batch)\b", r"\bnext (live )?class\b",
    r"என்\s*(வகுப்பு|அட்டவணை)", r"அடுத்த\s*வகுப்பு",
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text).lower().strip())


def _has(m, words):
    return any(w in m for w in words)


def route(msg: str):
    m = _norm(msg)
    if _has(m, SECURITY):
        return "human", "security"
    if any(re.search(p, m) for p in OTHER_PERSON):
        return "refuse", "privacy"
    if _has(m, BILLING):
        if _has(m, POLICY_HINTS) and not _has(m, CASE_HINTS):
            return "faq", None                    # general policy question
        return "human", "billing"
    if any(re.search(p, m) for p in PERSONAL):
        return "personal", None
    return "faq", None
