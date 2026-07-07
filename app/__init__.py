"""Mini Agent 应用包 — 启动时加载 .env。"""
from app import config as _config  # noqa: F401 — 确保 .env 优先加载
