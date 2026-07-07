from app.tools.base import Tool
from app.tools.workspace import (
    list_workspace_files,
    search_workspace_file,
    read_workspace_file,
    write_workspace_file,
)


class ListFilesTool(Tool):
    name = "list_files"
    description = "列出 workspace 工作区中所有可用文件"
    parameters = {"type": "object", "properties": {}, "required": []}

    def execute(self, args: dict) -> str:
        return "\n".join(list_workspace_files())


class SearchFileTool(Tool):
    name = "search_file"
    description = "按文件名搜索 workspace 中的文件"
    parameters = {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "要搜索的文件名或关键词"},
        },
        "required": ["filename"],
    }

    def execute(self, args: dict) -> str:
        result = search_workspace_file(args.get("filename", ""))
        return result or "未找到匹配文件"


class ReadFileTool(Tool):
    name = "read_file"
    description = "读取 workspace 中指定文件的内容"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件的相对路径，如 readme.txt"},
        },
        "required": ["path"],
    }

    def execute(self, args: dict) -> str:
        return read_workspace_file(args.get("path", ""))


class WriteFileTool(Tool):
    name = "write_file"
    description = "向 workspace 写入或覆盖文件"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件的相对路径"},
            "text": {"type": "string", "description": "要写入的内容"},
        },
        "required": ["path", "text"],
    }

    def execute(self, args: dict) -> str:
        return write_workspace_file(args.get("path", ""), args.get("text", ""))
