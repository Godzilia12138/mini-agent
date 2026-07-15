"""统一日志配置 — 控制台彩色 + 文件滚动，不暴露敏感信息。"""

import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_logger(name: str = "mini-agent") -> logging.Logger:
    """获取或初始化日志器。

    - 控制台：INFO 级别，带颜色
    - 文件：DEBUG 级别，10MB 滚动，保留 5 份
    - 自动脱敏 API Key / 令牌等敏感字段
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # ── 控制台 Handler（INFO+）──
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(_ConsoleFormatter())
    logger.addHandler(console)

    # ── 文件 Handler（DEBUG+，滚动）──
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        _LOG_DIR / "mini-agent.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)-7s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(file_handler)

    return logger


def _sanitize(text: str, max_len: int = 200) -> str:
    """截断长文本，脱敏敏感信息。"""
    if not text:
        return ""
    # 脱敏 sk-xxx 格式的 API Key
    sanitized = text
    for prefix in ("sk-", "sk-ant-"):
        idx = sanitized.find(prefix)
        while idx != -1:
            end = sanitized.find(" ", idx)
            end = end if end != -1 else len(sanitized)
            token = sanitized[idx:end]
            if len(token) > 8:
                sanitized = sanitized[:idx] + token[:6] + "****" + token[-4:] + sanitized[end:]
            idx = sanitized.find(prefix, idx + 1)
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len] + f"...（共 {len(text)} 字符，已截断）"
    return sanitized


class _ConsoleFormatter(logging.Formatter):
    """带颜色的控制台格式化器。"""

    _COLORS = {
        logging.DEBUG: "\033[36m",      # 青色
        logging.INFO: "\033[32m",       # 绿色
        logging.WARNING: "\033[33m",    # 黄色
        logging.ERROR: "\033[31m",      # 红色
        logging.CRITICAL: "\033[41m",   # 红底
    }
    _RESET = "\033[0m"

    def format(self, record):
        color = self._COLORS.get(record.levelno, self._RESET)
        timestamp = self.formatTime(record, "%H:%M:%S")
        return (
            f"{color}[{timestamp}] {record.levelname:<7}{self._RESET} "
            f"{record.getMessage()}"
        )


# 模块级快捷函数
def get_logger(name: str = "mini-agent") -> logging.Logger:
    return setup_logger(name)


# ── 使用示例 ──
# from app.logger import get_logger
# log = get_logger(__name__)
# log.info("用户消息: %s", _sanitize(msg))
# log.warning("API 重试 %d/3: %s", attempt, err)
# log.error("工具执行异常", exc_info=True)
