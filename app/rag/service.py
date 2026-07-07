from app.rag import indexer, retriever


class RAGService:
    """RAG 知识库统一入口。"""

    def index_document(self, source: str, text: str) -> int:
        return indexer.index_document(source, text)

    def index_workspace_file(self, path: str) -> int:
        return indexer.index_workspace_file(path)

    def search(self, query: str, top_k: int = 5) -> str:
        return retriever.rag_search(query, top_k=top_k)

    def stats(self) -> dict:
        return indexer.get_stats()

    def list_sources(self) -> list:
        return indexer.list_sources()


rag_service = RAGService()
