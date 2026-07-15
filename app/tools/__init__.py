"""Tool System — 统一注册与执行。"""
from app.logger import get_logger
from app.tools.registry import ToolRegistry
from app.tools.workspace import WORKSPACE, list_workspace_files
from app.tools.file_tools import (
    ListFilesTool,
    SearchFileTool,
    ReadFileTool,
    WriteFileTool,
)
from app.tools.calculator import CalculatorTool
from app.tools.extended_tools import DbQueryTool, WebSearchTool
from app.tools.rag_tools import RagSearchTool, RagIndexTool, RagStatusTool

log = get_logger(__name__)


def _build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(ListFilesTool())
    reg.register(SearchFileTool())
    reg.register(ReadFileTool())
    reg.register(WriteFileTool())
    reg.register(CalculatorTool())
    reg.register(DbQueryTool())
    reg.register(RagSearchTool())
    reg.register(RagIndexTool())
    reg.register(RagStatusTool())
    reg.register(WebSearchTool())
    # MCP 外部工具（可选，需 MCP_ENABLED 或 mcp_servers.json）
    try:
        from app.mcp.tool_adapter import register_mcp_tools
        register_mcp_tools(reg)
    except Exception as exc:
        log.warning("MCP 工具加载跳过: %s", exc)
    return reg


tool_registry = _build_registry()

# 向后兼容
TOOL_DEFINITIONS = tool_registry.get_definitions()


def list_files():
    return list_workspace_files()
