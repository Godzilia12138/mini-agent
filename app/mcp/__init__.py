"""MCP 集成：对外暴露工具 / 接入外部 MCP 服务。"""

from app.mcp.config import load_mcp_servers, mcp_enabled

__all__ = ["load_mcp_servers", "mcp_enabled"]
