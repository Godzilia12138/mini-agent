from app.config import env, default_model, provider_credentials
from app.providers.base import BaseModelProvider
from app.providers.openai_compat import OpenAICompatibleProvider

import requests


class ModelRouter:
    """模型路由：DeepSeek / Qwen / Kimi / GLM 等。"""

    def __init__(self):
        self._providers: dict[str, BaseModelProvider] = {}
        self._register_all()

    def _register(self, provider: BaseModelProvider):
        self._providers[provider.model_id] = provider

    def _add(self, model_id: str, provider_name: str, model_name: str, display_name: str):
        self._register(OpenAICompatibleProvider(
            model_id=model_id,
            model_name=model_name,
            display_name=display_name,
            provider_name=provider_name,
        ))

    def _register_kimi(self):
        """注册 Kimi 模型，并从 API 拉取账号可用列表。"""
        kimi_model = env("KIMI_MODEL", "moonshot-v1-32k")
        registered: set[str] = set()

        self._add("kimi", "kimi", kimi_model, f"Kimi · {kimi_model}")
        registered.add("kimi")

        fallback = [
            ("kimi-k2.6", "Kimi K2.6"),
            ("kimi-k2.5", "Kimi K2.5"),
            ("moonshot-v1-auto", "Kimi Auto"),
            ("moonshot-v1-32k", "Kimi 32K"),
            ("moonshot-v1-128k", "Kimi 128K"),
            ("moonshot-v1-8k", "Kimi 8K"),
        ]
        for mid, name in fallback:
            if mid not in registered:
                self._add(mid, "kimi", mid, name)
                registered.add(mid)

        api_key, base_url = provider_credentials("kimi")
        if not api_key:
            return
        try:
            res = requests.get(
                f"{base_url.rstrip('/')}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            if not res.ok:
                return
            for item in res.json().get("data", []):
                mid = item.get("id")
                if not mid or mid in registered:
                    continue
                if "vision" in mid:
                    continue
                self._add(mid, "kimi", mid, f"Kimi · {mid}")
                registered.add(mid)
        except Exception:
            pass

    def _register_all(self):
        env_model = default_model()

        # ── DeepSeek ──
        self._add("deepseek-chat", "deepseek", "deepseek-chat", "DeepSeek Chat")
        self._add(env_model, "deepseek", env_model, f"DeepSeek · {env_model}")

        # ── Qwen ──
        qwen_model = env("QWEN_MODEL", "qwen-plus")
        self._add("qwen", "qwen", qwen_model, f"Qwen · {qwen_model}")
        self._add("qwen-plus", "qwen", "qwen-plus", "Qwen Plus")
        self._add("qwen-turbo", "qwen", "qwen-turbo", "Qwen Turbo")
        self._add("qwen-max", "qwen", "qwen-max", "Qwen Max")

        # ── Kimi (Moonshot) ──
        self._register_kimi()

        # ── GLM (智谱) ──
        glm_model = env("GLM_MODEL", "glm-4-flash")
        self._add("glm", "glm", glm_model, f"GLM · {glm_model}")
        self._add("glm-4-flash", "glm", "glm-4-flash", "GLM-4 Flash")
        self._add("glm-4", "glm", "glm-4", "GLM-4")
        self._add("glm-4-plus", "glm", "glm-4-plus", "GLM-4 Plus")

        # ── OpenAI（可选）──
        self._add("gpt-4o-mini", "openai", "gpt-4o-mini", "GPT-4o Mini")

    @property
    def default_model_id(self) -> str:
        mid = default_model()
        if mid in self._providers and self._providers[mid].is_available():
            return mid
        for pid, p in self._providers.items():
            if p.is_available():
                return pid
        return mid

    def list_models(self) -> list[dict]:
        default = self.default_model_id
        groups = {"deepseek": 0, "qwen": 1, "kimi": 2, "glm": 3, "openai": 4, "other": 5}

        def sort_key(p):
            pid = p.model_id
            if pid.startswith("deepseek") or "deepseek" in p.display_name.lower():
                g = groups["deepseek"]
            elif "qwen" in pid or "Qwen" in p.display_name:
                g = groups["qwen"]
            elif (
                pid == "kimi"
                or pid.startswith("moonshot")
                or pid.startswith("kimi-k")
                or "Kimi" in p.display_name
            ):
                g = groups["kimi"]
            elif "glm" in pid or "GLM" in p.display_name:
                g = groups["glm"]
            elif "gpt" in pid:
                g = groups["openai"]
            else:
                g = groups["other"]
            return (not (p.model_id == default), g, p.model_id)

        result = []
        for p in sorted(self._providers.values(), key=sort_key):
            info = p.to_dict()
            info["is_default"] = p.model_id == default
            result.append(info)
        return result

    def get_provider(self, model_id: str | None = None) -> BaseModelProvider:
        mid = model_id or self.default_model_id
        provider = self._providers.get(mid)
        if not provider:
            available = [k for k, v in self._providers.items() if v.is_available()]
            raise ValueError(f"未知模型: {mid}，可用: {', '.join(available) or '无'}")
        return provider

    def resolve_model_id(self, model_id: str | None) -> str:
        if model_id and model_id in self._providers:
            return model_id
        return self.default_model_id


model_router = ModelRouter()
