from app.rag.chunker import chunk_text
from app.rag.store import RagStore

_store: RagStore | None = None


def get_store() -> RagStore:
    global _store
    if _store is None:
        _store = RagStore()
    return _store


def index_document(source: str, text: str, chunk_size: int = 500) -> int:
    chunks = chunk_text(text, chunk_size=chunk_size)
    return get_store().add_document(source, chunks)


def search(query: str, top_k: int = 5) -> list[dict]:
    return get_store().search(query, top_k=top_k)


def list_sources() -> list[dict]:
    return get_store().list_sources()


def get_stats() -> dict:
    return get_store().stats()


def index_workspace_file(path: str) -> int:
    from app.tools.workspace import read_workspace_file
    text = read_workspace_file(path)
    if text.startswith("文件不存在"):
        raise FileNotFoundError(text)
    return index_document(path, text)
