"""Module 10: evaluation. Run:  python -m eval.run_eval          (full pipeline, needs the model)
python -m eval.run_eval --router-only   (no model needed)"""
import csv, sys, statistics, pathlib, tempfile
import numpy as np
from collections import defaultdict
from app import pipeline, tickets, ingest, seed_db
from app.router import route

tickets.PATH = pathlib.Path(tempfile.mkdtemp()) / "eval_tickets.jsonl"   # keep eval tickets separate
OTHER_STUDENT_TITLES = ["Data Science Intro", "Statistics Lab", "Web Development"]
ROUTER_ONLY = "--router-only" in sys.argv

rows = list(csv.DictReader(open("eval/golden_set.csv", encoding="utf-8")))
seed_db.seed()

if ROUTER_ONLY:
    class _R:                                   # stand-in: never reached for non-FAQ rows
        def search(self, *a, **k): return []
        def embed_query(self, q): return np.zeros((1, 4), dtype="float32")
    retriever, rows = _R(), [r for r in rows if r["expected_action"] in ("human", "personal", "refuse")]
else:
    if not pathlib.Path("data/chunks.json").exists():
        ingest.build()
    from app.retriever import Retriever
    retriever = Retriever()
from app.cache import SemanticCache
cache = SemanticCache(retriever)

results, latencies, leaks = [], [], 0
for r in rows:
    res = pipeline.answer(r["question"], 1, retriever, cache)       # always logged in as student 1
    latencies.append(res["latency_ms"])
    exp = r["expected_action"]
    got = res["action"]
    if exp == "answer":
        ok = got in ("answer", "confirm") and r["expected_source"] in res.get("source", "")
    elif exp == "fallback":
        ok = got == "fallback"
    else:
        ok = got == exp
    if any(t in res["reply"] for t in OTHER_STUDENT_TITLES):
        leaks += 1
    results.append((r, got, ok))

def pct(a, b): return f"{a}/{b} = {100 * a / b:.0f}%" if b else "n/a"

print("\n=== Evaluation ===")
by_exp = defaultdict(list)
for r, got, ok in results:
    by_exp[r["expected_action"]].append(ok)
for exp, oks in by_exp.items():
    print(f"{exp:9s} correct: {pct(sum(oks), len(oks))}")
esc = [ok for r, g, ok in results if r["expected_action"] == "human"]
print(f"\nESCALATION RECALL (billing/security -> human): {pct(sum(esc), len(esc))}")
print(f"CROSS-STUDENT LEAKS: {leaks}   (must be 0)")
for lang in ("en", "ta"):
    xs = [ok for r, g, ok in results if r["language"] == lang]
    print(f"overall accuracy [{lang}]: {pct(sum(xs), len(xs))}")
print(f"latency ms: median={statistics.median(latencies):.1f}  p95={np.percentile(latencies, 95):.1f}"
f"  max={max(latencies):.1f}   (target < 3000)")
bad = [(r["question"], r["expected_action"], g) for r, g, ok in results if not ok]
print(f"\nFailures ({len(bad)}):")
for q, e, g in bad:
    print(f"  expected {e:9s} got {g:9s} | {q}")
