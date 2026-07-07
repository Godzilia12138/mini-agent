"""
Mini Agent MCP Server（stdio）

供 Cursor / Claude Desktop 等 MCP 客户端调用本项目的 Agent 工具。

启动：
  python -m app.mcp.server
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from app.tools import tool_registry

mcp = FastMCP(
    "mini-agent",
    instructions=(
        "Mini Agent 工具服务：workspace 文件读写、计算器、RAG 知识库检索、"
        "会话统计等。所有文件操作在 workspace/ 目录内。"
    ),
)


def _exec(tool_name: str, **kwargs) -> str:
    return tool_registry.execute(tool_name, kwargs)


@mcp.tool()
def list_files() -> str:
    """列出 workspace 工作区中所有可用文件"""
    return _exec("list_files")


@mcp.tool()
def search_file(filename: str) -> str:
    """按文件名搜索 workspace 中的文件"""
    return _exec("search_file", filename=filename)


@mcp.tool()
def read_file(path: str) -> str:
    """读取 workspace 中指定文件的内容"""
    return _exec("read_file", path=path)


@mcp.tool()
def write_file(path: str, text: str) -> str:
    """向 workspace 写入或覆盖文件"""
    return _exec("write_file", path=path, text=text)


@mcp.tool()
def calculator(expression: str) -> str:
    """计算数学表达式，支持 + - * / // % ** 和括号"""
    return _exec("calculator", expression=expression)


@mcp.tool()
def db_query(action: str) -> str:
    """查询系统数据库：action=session_count 或 list_sessions"""
    return _exec("db_query", action=action)


@mcp.tool()
def rag_search(query: str, top_k: int = 5) -> str:
    """在 RAG 知识库中语义检索相关文档片段"""
    return _exec("rag_search", query=query, top_k=top_k)


@mcp.tool()
def rag_index(path: str) -> str:
    """将 workspace 文件索引到 RAG 知识库"""
    return _exec("rag_index", path=path)


@mcp.tool()
def rag_status() -> str:
    """查看 RAG 知识库索引状态"""
    return _exec("rag_status")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
