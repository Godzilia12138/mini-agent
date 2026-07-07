"""统一配置：始终从项目根目录加载 .env。"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"

_loaded = False


def ensure_env() -> Path:
    global _loaded
    if not _loaded:
        if ENV_FILE.is_file():
            load_dotenv(ENV_FILE, override=True)
        _loaded = True
    return ENV_FILE


def env(key: str, default: str = "") -> str:
    ensure_env()
    value = os.getenv(key, default)
    if value:
        value = value.strip().strip("\ufeff").strip('"').strip("'")
    return value


def env_bool(key: str, default: bool = False) -> bool:
    return env(key, str(default)).lower() in ("1", "true", "yes", "on")


def normalize_base_url(url: str) -> str:
    """统一为 OpenAI 兼容 base_url（不含 /chat/completions）。"""
    if not url:
        return ""
    url = url.strip().rstrip("/")
    for suffix in ("/chat/completions", "/completions"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url.rstrip("/")


def _first_env(*keys: str, default: str = "") -> str:
    for key in keys:
        val = env(key)
        if val:
            return val
    return default


def provider_credentials(provider: str) -> tuple[str, str]:
    """
    读取各厂商 API Key 与 Base URL。
    每个厂商必须使用独立变量名，不能共用 API_KEY。
    """
    configs = {
        "deepseek": {
            "keys": ("DEEPSEEK_API_KEY", "API_KEY"),
            "urls": ("DEEPSEEK_BASE_URL", "BASE_URL"),
            "default_url": "https://api.deepseek.com/v1",
        },
        "qwen": {
            "keys": ("QWEN_API_KEY", "DASHSCOPE_API_KEY"),
            "urls": ("QWEN_BASE_URL", "QWEN_API_URL", "DASHSCOPE_BASE_URL"),
            "default_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        },
        "glm": {
            "keys": ("GLM_API_KEY",),
            "urls": ("GLM_BASE_URL", "GLM_API_URL"),
            "default_url": "https://open.bigmodel.cn/api/paas/v4",
        },
        "kimi": {
            "keys": ("KIMI_API_KEY", "MOONSHOT_API_KEY"),
            "urls": ("KIMI_BASE_URL", "KIMI_API_URL", "MOONSHOT_BASE_URL"),
            "default_url": "https://api.moonshot.cn/v1",
        },
        "openai": {
            "keys": ("OPENAI_API_KEY",),
            "urls": ("OPENAI_BASE_URL",),
            "default_url": "https://api.openai.com/v1",
        },
    }
    cfg = configs.get(provider, {})
    api_key = _first_env(*cfg.get("keys", ()), default="")
    base_url = normalize_base_url(
        _first_env(*cfg.get("urls", ()), default=cfg.get("default_url", ""))
    )
    return api_key, base_url


def default_model() -> str:
    return env("MODEL") or env("DEFAULT_MODEL", "deepseek-v4-flash")


ensure_env()
