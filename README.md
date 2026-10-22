# 🎓 Bilingual (English / தமிழ்) Student Support Assistant

A retrieval-based support assistant for an EdTech platform (50,000 students). It answers
**only from approved help-center articles**, escalates billing / refund / account-security
issues to a human, supports English, Tamil and Tanglish, and runs fully locally
(**no external LLM API**, so monthly cost is fixed hardware cost).

## Tech stack
Python · FastAPI · Streamlit · sentence-transformers · FAISS · SQLite · PyJWT · pytest · Docker

## Architecture

```
Student message (authenticated via JWT)
  -> language detection (EN / TA / Tanglish)
  -> guardrail router
       |- billing / security case -> human handoff + ticket (no bot answer)
       |- other person's data      -> polite refusal
       |- "my schedule"            -> read-only DB tool bound to the token's student_id
       '- everything else          -> semantic cache -> FAISS retrieval (multilingual-e5-small)
                                        -> 3-zone confidence decision
                                           >=0.84 answer + source | 0.80-0.84 "did you mean?" | <0.80 handoff
```

## Highlights

- **Bilingual search:** English, Tamil and Tanglish (Tamil in English letters), using
  multilingual embeddings (`multilingual-e5-small`) with FAISS vector search.
- **Approved content only:** replies are the help articles themselves, shown with their
  source file, so the bot cannot invent policy.
- **Safe escalation:** billing, refund and account-security messages skip the bot and create
  a prioritized support ticket for a human agent.
- **Student data isolation:** identity comes from a signed JWT, never from the chat text.
  Student data is read through a read-only, parameterized database tool, and the search index
  contains no personal data. Requests for another student's information are refused.
- **Calibrated confidence:** a three-zone decision (answer / "did you mean?" / hand off), with
  a lexical gate that stops off-topic questions from receiving a loosely related article.
- **Production habits:** semantic cache, per-student rate limiting, PII-redacted logs and tickets

## Run it

```bash
python -m venv venv && venv\Scripts\activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

python -m app.ingest          # builds data/chunks.json (64 chunks)
python -m app.seed_db         # fake students + classes

uvicorn app.main:app --reload            # terminal 1  (API docs at http://localhost:8000/docs)
streamlit run ui/chat.py                 # terminal 2  (chat UI)
```

## Test and evaluate

```bash
python -m pytest tests -v                 # 49 tests: router, isolation, auth, pipeline
python -m eval.run_eval                   # full evaluation on eval/golden_set.csv
python -m eval.run_eval --router-only     # no model needed
```

## Results (54-question bilingual golden set)

| Metric | Result |
|---|---|
| Escalation recall (billing and security) | 10/10 |
| Cross-student data leaks | 0 |
| Retrieval accuracy on answerable questions | 30/32 (tuned set; held-out evaluation in progress) |
| p95 latency (CPU only) | ~130 ms |
| Automated tests | 54 |

## Limitations
Keyword escalation rules are brittle on unseen wording (a trained intent classifier is the next step),
answers are extractive rather than conversational, and the Tamil articles need native-speaker review.

## Possible extensions
BM25 hybrid search, trained intent classifier, local LLM rephrasing (compare Tamil accuracy first),
Django admin for article approval, Postgres, Redis cache.


