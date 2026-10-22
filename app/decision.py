"""Three-zone confidence decision (no heavy imports, easy to test)."""
ANSWER_T = 0.84   # confident -> answer directly      (tuned for multilingual-e5-small)
MAYBE_T = 0.80    # unsure    -> ask the student to confirm


def decide(hits):
    """Return (action, best_hit): 'answer' | 'confirm' | 'fallback'."""
    if not hits:
        return "fallback", None
    s = hits[0]["score"]
    if s >= ANSWER_T:
        return "answer", hits[0]
    if s >= MAYBE_T:
        return "confirm", hits[0]
    return "fallback", None
