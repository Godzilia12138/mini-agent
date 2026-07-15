"""将 MCP 外部工具注册到 ToolRegistry。"""

from __future__ import annotations

from app.tools.base import Tool
from app.tools.registry import ToolRegistry
from app.logger import get_logger

log = get_logger(__name__)


class MCPTool(Tool):
    """包装 MCP Bridge 上的远程工具。"""

    def __init__(self, name: str, description: str, parameters: dict, bridge, remote_name: str):
        self.name = name
        self.description = description
        self.parameters = parameters
        self._bridge = bridge
        self._remote_name = remote_name

    def execute(self, args: dict) -> str:
        return self._bridge.call_tool(self.name, args)


_mcp_registered = False


def register_mcp_tools(registry: ToolRegistry) -> int:
    """连接 MCP 服务器并将远程工具注入 registry。返回注册数量。"""
    global _mcp_registered
    from app.mcp.config import load_mcp_servers, mcp_enabled
    from app.mcp.bridge import get_mcp_bridge

    if not mcp_enabled():
        return 0

    servers = load_mcp_servers()
    if not servers:
        return 0

    bridge = get_mcp_bridge()
    if not bridge.tools:
        ok = bridge.start(servers)
        if not ok and bridge.error:
            log.warning("MCP 连接失败: %s", bridge.error)

    count = 0
    for tool_name, meta in bridge.tools.items():
        if registry.get(tool_name):
            continue
        try:
            registry.register(
                MCPTool(
                    name=tool_name,
                    description=f"[MCP] {meta['description']}",
                    parameters=meta["parameters"],
                    bridge=bridge,
                    remote_name=meta.get("remote_name", tool_name),
                )
            )
            count += 1
        except ValueError:
            pass

    _mcp_registered = count > 0
    return count


def mcp_tools_registered() -> bool:
    return _mcp_registered
