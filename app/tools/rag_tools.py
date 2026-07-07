from app.tools.base import Tool
from app.rag.service import rag_service


class RagSearchTool(Tool):
    name = "rag_search"
    description = "在知识库中进行语义检索，查找与问题相关的文档片段（上传的文件会自动入库）"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "检索问题或关键词"},
            "top_k": {"type": "integer", "description": "返回条数，默认 5"},
        },
        "required": ["query"],
    }

    def execute(self, args: dict) -> str:
        query = args.get("query", "").strip()
        if not query:
            return "请提供检索 query"
        top_k = int(args.get("top_k") or 5)
        stats = rag_service.stats()
        if stats["total_chunks"] == 0:
            return "知识库为空，请先上传文件（会自动索引）或使用 rag_index 索引 workspace 文件。"
        return rag_service.search(query, top_k=top_k)


class RagIndexTool(Tool):
    name = "rag_index"
    description = "将 workspace 中的文件加入 RAG 知识库索引，便于后续语义检索"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "workspace 内文件相对路径"},
        },
        "required": ["path"],
    }

    def execute(self, args: dict) -> str:
        path = args.get("path", "").strip()
        if not path:
            return "请提供文件路径"
        try:
            count = rag_service.index_workspace_file(path)
            return f"已将 {path} 索引到知识库，共 {count} 个文本块。"
        except FileNotFoundError as e:
            return str(e)
        except Exception as e:
            return f"索引失败: {e}"


class RagStatusTool(Tool):
    name = "rag_status"
    description = "查看 RAG 知识库状态（已索引文件数和文本块数）"
    parameters = {"type": "object", "properties": {}, "required": []}

    def execute(self, args: dict) -> str:
        stats = rag_service.stats()
        if stats["total_chunks"] == 0:
            return "知识库为空，暂无索引。"
        lines = [f"共 {stats['total_chunks']} 个文本块，来自 {len(stats['sources'])} 个文件："]
        for s in stats["sources"]:
            lines.append(f"- {s['source']}（{s['chunks']} 块）")
        return "\n".join(lines)
