import json
import os
import threading

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "rag")
CHUNKS_FILE = os.path.join(DATA_DIR, "chunks.json")
VECTORIZER_FILE = os.path.join(DATA_DIR, "vectorizer.joblib")
FAISS_FILE = os.path.join(DATA_DIR, "index.faiss")
META_FILE = os.path.join(DATA_DIR, "meta.json")

_lock = threading.RLock()


def _embedding_mode() -> str:
    return env("RAG_EMBEDDING_MODE", "tfidf").lower()


class RagStore:
    """RAG 向量库：默认 TF-IDF（零依赖下载），可选 FAISS + API/本地 embedding。"""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.chunks: list[dict] = []
        self.vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2))
        self.matrix = None
        self.faiss_index = None
        self._dim = 0
        self._mode = _embedding_mode()
        self._load()

    def _load(self):
        if os.path.exists(CHUNKS_FILE):
            with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)

        if self._mode == "tfidf" and self.chunks:
            if os.path.exists(VECTORIZER_FILE):
                self.vectorizer = joblib.load(VECTORIZER_FILE)
            texts = [c["text"] for c in self.chunks]
            self.matrix = self.vectorizer.transform(texts)
        elif self._mode in ("api", "local") and self.chunks:
            self._load_faiss()

    def _load_faiss(self):
        import faiss
        if os.path.exists(FAISS_FILE) and os.path.exists(META_FILE):
            with open(META_FILE, "r") as f:
                meta = json.load(f)
            self._dim = meta.get("dim", 0)
            self.faiss_index = faiss.read_index(FAISS_FILE)

    def _save(self):
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

        if self._mode == "tfidf" and self.matrix is not None:
            joblib.dump(self.vectorizer, VECTORIZER_FILE)
        elif self.faiss_index is not None and self.faiss_index.ntotal > 0:
            import faiss
            faiss.write_index(self.faiss_index, FAISS_FILE)
            with open(META_FILE, "w") as f:
                json.dump({"dim": self._dim, "mode": self._mode}, f)

    def _rebuild_index(self):
        if not self.chunks:
            self.matrix = None
            self.faiss_index = None
            self._dim = 0
            return

        texts = [c["text"] for c in self.chunks]
        mode = _embedding_mode()
        self._mode = mode

        if mode == "tfidf":
            self.matrix = self.vectorizer.fit_transform(texts)
            self.faiss_index = None
            self._dim = self.matrix.shape[1]
        else:
            from app.rag.embedder import embed_dense
            import faiss

            vectors = embed_dense(texts)
            if vectors is None:
                # 回退 TF-IDF
                self._mode = "tfidf"
                self.matrix = self.vectorizer.fit_transform(texts)
                self.faiss_index = None
                self._dim = self.matrix.shape[1]
            else:
                self.matrix = None
                self._dim = vectors.shape[1]
                self.faiss_index = faiss.IndexFlatIP(self._dim)
                self.faiss_index.add(vectors)

        self._save()

    def remove_source(self, source: str) -> int:
        before = len(self.chunks)
        self.chunks = [c for c in self.chunks if c["source"] != source]
        removed = before - len(self.chunks)
        if removed:
            self._rebuild_index()
        return removed

    def add_document(self, source: str, texts: list[str]) -> int:
        if not texts:
            return 0

        with _lock:
            self.remove_source(source)
            base_id = len(self.chunks)
            for i, text in enumerate(texts):
                self.chunks.append({
                    "id": base_id + i,
                    "source": source,
                    "chunk_index": i,
                    "text": text,
                })
            self._rebuild_index()
            return len(texts)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        with _lock:
            if not self.chunks:
                return []

            top_k = min(top_k, len(self.chunks))

            if self._mode == "tfidf" and self.matrix is not None:
                qv = self.vectorizer.transform([query])
                scores = cosine_similarity(qv, self.matrix)[0]
                indices = scores.argsort()[-top_k:][::-1]
                score_vals = scores[indices]
            elif self.faiss_index is not None:
                from app.rag.embedder import embed_dense
                qv = embed_dense([query])
                if qv is None:
                    return []
                score_vals, indices = self.faiss_index.search(qv, top_k)
                indices = indices[0]
                score_vals = score_vals[0]
            else:
                return []

            results = []
            for score, idx in zip(score_vals, indices):
                idx = int(idx)
                if idx < 0 or idx >= len(self.chunks):
                    continue
                chunk = self.chunks[idx]
                results.append({
                    "source": chunk["source"],
                    "text": chunk["text"],
                    "score": float(score),
                    "chunk_index": chunk["chunk_index"],
                })
            return results

    def list_sources(self) -> list[dict]:
        stats: dict[str, int] = {}
        for c in self.chunks:
            stats[c["source"]] = stats.get(c["source"], 0) + 1
        return [{"source": k, "chunks": v} for k, v in sorted(stats.items())]

    def stats(self) -> dict:
        return {
            "total_chunks": len(self.chunks),
            "sources": self.list_sources(),
            "embedding_mode": self._mode,
            "embedding_dim": self._dim,
        }
