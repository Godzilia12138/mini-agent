"""MCP 客户端配置加载。"""

import json
from pathlib import Path

from app.config import ROOT_DIR, env, env_bool

MCP_CONFIG_FILE = ROOT_DIR / "mcp_servers.json"


def load_mcp_servers() -> list[dict]:
    """
    读取 MCP 客户端配置。
    优先 mcp_servers.json，其次 .env 的 MCP_SERVERS（JSON 数组）。
    """
    if MCP_CONFIG_FILE.is_file():
        try:
            data = json.loads(MCP_CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [s for s in data if isinstance(s, dict) and s.get("name")]
        except json.JSONDecodeError:
            pass

    raw = env("MCP_SERVERS", "")
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [s for s in data if isinstance(s, dict) and s.get("name")]
        except json.JSONDecodeError:
            pass
    return []


def mcp_enabled() -> bool:
    if env_bool("MCP_ENABLED", False):
        return True
    return bool(load_mcp_servers())
