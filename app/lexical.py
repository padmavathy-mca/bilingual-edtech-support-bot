import re

# Tamil range is included explicitly: Python's \w splits Tamil words at vowel signs
WORD = re.compile(r"[\w\u0B80-\u0BFF]+")
STOP = set("""a an the is are was were be to of in on for and or do does did how what when where
which who why can i my me you your it this that with at by from have has had there any about
please write tell best give show get would could should will not no
எப்படி என்ன எங்கே எப்போது ஏன் எது என் எனது உங்கள் செய்வது முடியுமா""".split())


def _content_words(text):
    return [w for w in WORD.findall(text.lower()) if w not in STOP]


def _match(q, c):
    return q == c or (len(q) >= 4 and len(c) >= 4 and (c.startswith(q) or q.startswith(c)))


def lexical_support(query, chunk_text, min_ratio=0.5):
    """True if at least half the query's content words appear in the article."""
    q = _content_words(query)
    if not q:
        return False
    c = set(_content_words(chunk_text))
    hits = sum(any(_match(w, x) for x in c) for w in q)
    return hits >= 1 and hits / len(q) >= min_ratio