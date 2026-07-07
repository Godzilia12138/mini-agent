import numpy as np
import requests

from app.config import env


def embed_dense(texts: list[str]) -> np.ndarray | None:
    """API 或本地模型生成稠密向量（用于 FAISS 模式）。"""
    mode = env("RAG_EMBEDDING_MODE", "tfidf").lower()

    if mode == "api":
        vectors = _embed_api(texts)
        if vectors is not None:
            return vectors

    if mode == "local":
        try:
            return _embed_local(texts)
        except Exception:
            return None

    return None


def _embed_api(texts: list[str]) -> np.ndarray | None:
    api_key = env("EMBEDDING_API_KEY") or env("OPENAI_API_KEY")
    if not api_key:
        return None

    base_url = env("EMBEDDING_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = env("EMBEDDING_MODEL", "text-embedding-3-small")

    res = requests.post(
        f"{base_url}/embeddings",
        json={"model": model, "input": texts},
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=60,
    )
    if not res.ok:
        return None

    data = sorted(res.json()["data"], key=lambda x: x["index"])
    vectors = np.array([d["embedding"] for d in data], dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return vectors / norms


_local_model = None


def _embed_local(texts: list[str]) -> np.ndarray:
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        model_name = env("RAG_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
        _local_model = SentenceTransformer(model_name)

    vectors = _local_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.array(vectors, dtype=np.float32)
