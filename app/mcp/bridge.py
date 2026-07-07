"""MCP 客户端桥接：连接外部 MCP Server，将工具注入 ToolRegistry。"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Any

from mcp.client.session_group import ClientSessionGroup, SseServerParameters, StdioServerParameters
from mcp.types import CallToolResult, TextContent


def _format_call_result(result: CallToolResult) -> str:
    parts: list[str] = []
    if result.isError:
        parts.append("[MCP 错误]")
    for block in result.content or []:
        if isinstance(block, TextContent):
            parts.append(block.text)
        elif hasattr(block, "text"):
            parts.append(getattr(block, "text", str(block)))
        else:
            parts.append(str(block))
    return "\n".join(parts) if parts else "(空响应)"


def _mcp_schema_to_openai(input_schema: dict | None) -> dict:
    schema = input_schema or {"type": "object", "properties": {}}
    if schema.get("type") != "object":
        schema = {"type": "object", "properties": {"input": schema}}
    schema.setdefault("properties", {})
    schema.setdefault("type", "object")
    return schema


class MCPBridge:
    """在后台线程维持 MCP 连接，供同步 Agent 调用。"""

    def __init__(self):
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._group: ClientSessionGroup | None = None
        self._ready = threading.Event()
        self._tools: dict[str, dict[str, Any]] = {}
        self._servers: list[dict] = []
        self._error: str | None = None
        self._started = False

    @property
    def tools(self) -> dict[str, dict[str, Any]]:
        return dict(self._tools)

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def servers(self) -> list[dict]:
        return list(self._servers)

    def start(self, servers: list[dict], timeout: float = 60.0) -> bool:
        if self._started:
            return bool(self._tools)
        if not servers:
            return False

        self._servers = servers
        self._thread = threading.Thread(target=self._thread_main, args=(servers,), daemon=True)
        self._thread.start()
        self._ready.wait(timeout=timeout)
        self._started = True
        return bool(self._tools) and not self._error

    def _thread_main(self, servers: list[dict]):
        try:
            asyncio.run(self._async_main(servers))
        except Exception as exc:
            self._error = str(exc)
            self._ready.set()

    async def _async_main(self, servers: list[dict]):
        self._loop = asyncio.get_running_loop()

        def name_hook(name: str, server_info) -> str:
            server_name = getattr(server_info, "name", None) or "mcp"
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in server_name)
            return f"mcp_{safe}__{name}"

        try:
            async with ClientSessionGroup(component_name_hook=name_hook) as group:
                for cfg in servers:
                    params = _build_server_params(cfg)
                    if params is None:
                        continue
                    await group.connect_to_server(params)

                for tool_name, tool in group.tools.items():
                    self._tools[tool_name] = {
                        "name": tool_name,
                        "remote_name": tool.name,
                        "description": tool.description or f"MCP 工具 {tool.name}",
                        "parameters": _mcp_schema_to_openai(tool.inputSchema),
                    }

                self._group = group
                self._ready.set()
                await asyncio.Future()
        except Exception as exc:
            self._error = str(exc)
            self._ready.set()

    def call_tool(self, name: str, arguments: dict) -> str:
        if not self._group or not self._loop:
            return f"MCP 未就绪: {self._error or '未连接'}"
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._group.call_tool(name, arguments),
                self._loop,
            )
            result = future.result(timeout=120)
            return _format_call_result(result)
        except Exception as exc:
            return f"MCP 调用失败: {exc}"

    def status(self) -> dict:
        return {
            "connected": bool(self._group and self._tools),
            "error": self._error,
            "servers": [
                {"name": s.get("name"), "transport": s.get("transport", "stdio")}
                for s in self._servers
            ],
            "tools": [
                {"name": t["name"], "description": t["description"][:80]}
                for t in self._tools.values()
            ],
        }


def _build_server_params(cfg: dict):
    transport = (cfg.get("transport") or "stdio").lower()
    if transport == "stdio":
        command = cfg.get("command")
        if not command:
            return None
        return StdioServerParameters(
            command=command,
            args=cfg.get("args") or [],
            env=cfg.get("env"),
        )
    if transport in ("sse", "http"):
        url = cfg.get("url")
        if not url:
            return None
        return SseServerParameters(url=url, headers=cfg.get("headers"))
    return None


_bridge: MCPBridge | None = None
_bridge_lock = threading.Lock()


def get_mcp_bridge() -> MCPBridge:
    global _bridge
    with _bridge_lock:
        if _bridge is None:
            _bridge = MCPBridge()
        return _bridge


def reload_mcp_bridge() -> dict:
    """重新加载 MCP 连接（需重启 Agent 进程后工具才完全刷新）。"""
    global _bridge
    with _bridge_lock:
        _bridge = MCPBridge()
        bridge = _bridge
    from app.mcp.config import load_mcp_servers, mcp_enabled

    if not mcp_enabled():
        return bridge.status()
    servers = load_mcp_servers()
    bridge.start(servers)
    return bridge.status()
