"""Module 3: embeddings + FAISS search."""
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class Retriever:
    def __init__(self, chunks_path="data/chunks.json",
                model_name="intfloat/multilingual-e5-small"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        with open(chunks_path, encoding="utf-8") as f:
            self.chunks = json.load(f)
        vecs = self.model.encode(
            [self._prefix("passage") + c["text"] for c in self.chunks],
            normalize_embeddings=True).astype("float32")
        self.index = faiss.IndexFlatIP(vecs.shape[1])   # inner product = cosine
        self.index.add(vecs)

    def _prefix(self, kind: str) -> str:
        return f"{kind}: " if "e5" in self.model_name else ""

    def embed_query(self, query: str):
        return self.model.encode([self._prefix("query") + query], normalize_embeddings=True).astype("float32")

    def search(self, query: str, k: int = 3, threshold: float = 0.0, lang: str = None):
        n = min(30, len(self.chunks))
        scores, ids = self.index.search(self.embed_query(query), n)
        hits = [{**self.chunks[i], "score": float(s)}
                for s, i in zip(scores[0], ids[0]) if s >= threshold]
        if lang:
            hits = [h for h in hits if h["lang"] == lang]
        return hits[:k]

