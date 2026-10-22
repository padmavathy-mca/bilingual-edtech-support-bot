"""Module 2: detect English / Tamil / Tanglish (Tamil written in English letters)."""
import re

TAMIL = re.compile(r"[\u0B80-\u0BFF]")
TANGLISH = {"pannunga", "panna", "varala", "vara", "enna", "eppadi", "epdi", "epo",
            "venum", "illa", "seiya", "sollunga", "kudunga", "irukku", "ennaku",
            "enakku", "paisa", "panam", "vapas", "kaasu", "puriyala", "theriyala"}


def detect_language(text: str) -> str:
    if TAMIL.search(text):
        return "ta"
    if set(re.findall(r"[a-z]+", text.lower())) & TANGLISH:
        return "tanglish"
    return "en"
