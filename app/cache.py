"""Module 5: semantic cache (non-personal answers only, per language)."""
import numpy as np


class SemanticCache:
    def __init__(self, retriever, threshold=0.95, max_size=1000):
        self.r, self.t, self.max = retriever, threshold, max_size
        self.vecs, self.langs, self.answers = [], [], []
        self.hits = self.misses = 0

    def get(self, query, lang):
        idx = [i for i, l in enumerate(self.langs) if l == lang]
        if idx:
            mat = np.vstack([self.vecs[i] for i in idx])
            sims = (mat @ self.r.embed_query(query).T).ravel()
            j = int(sims.argmax())
            if sims[j] >= self.t:
                self.hits += 1
                return self.answers[idx[j]]
        self.misses += 1
        return None

    def put(self, query, lang, answer):
        if len(self.vecs) >= self.max:
            self.vecs.pop(0); self.langs.pop(0); self.answers.pop(0)
        self.vecs.append(self.r.embed_query(query))
        self.langs.append(lang); self.answers.append(answer)
