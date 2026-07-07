from app.providers.base import BaseModelProvider


class StubProvider(BaseModelProvider):
    """预留模型，尚未实现。"""

    def __init__(self, model_id: str, display_name: str, reason: str = "即将推出"):
        self.model_id = model_id
        self.display_name = display_name
        self.reason = reason

    def is_available(self) -> bool:
        return False

    def chat(self, messages, tools=None, temperature=0.7):
        raise NotImplementedError(f"{self.display_name} {self.reason}")

    def chat_stream(self, messages, tools=None, temperature=0.7):
        raise NotImplementedError(f"{self.display_name} {self.reason}")
        yield  # noqa: make generator
