from app.tools.base import Tool


class DbQueryTool(Tool):
    name = "db_query"
    description = "查询系统数据库中的会话统计信息"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["session_count", "list_sessions"],
                "description": "session_count=会话总数, list_sessions=列出会话标题",
            },
        },
        "required": ["action"],
    }

    def execute(self, args: dict) -> str:
        from app import persistence

        action = args.get("action", "session_count")
        sessions = persistence.list_sessions()

        if action == "session_count":
            return f"当前共有 {len(sessions)} 个会话"

        if action == "list_sessions":
            if not sessions:
                return "暂无会话记录"
            lines = [
                f"- {s['title']}（{s['message_count']} 条消息，模型: {s.get('model', '未知')}）"
                for s in sessions[:20]
            ]
            suffix = f"\n... 共 {len(sessions)} 个会话" if len(sessions) > 20 else ""
            return "\n".join(lines) + suffix

        return f"未知 action: {action}"


class WebSearchTool(Tool):
    name = "web_search"
    description = "搜索互联网获取最新信息（预留）"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"},
        },
        "required": ["query"],
    }

    def execute(self, args: dict) -> str:
        return (
            f"网页搜索功能尚未启用。（查询: {args.get('query', '')}）"
            "请基于已有文件和知识回答，或告知用户该功能即将推出。"
        )
