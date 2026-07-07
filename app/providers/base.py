from abc import ABC, abstractmethod
from typing import Iterator


class BaseModelProvider(ABC):
    """模型 Provider 抽象基类。"""

    model_id: str
    display_name: str

    @abstractmethod
    def is_available(self) -> bool:
        """API Key 等是否已配置。"""

    @abstractmethod
    def chat(self, messages: list, tools=None, temperature: float = 0.7) -> dict:
        """非流式调用，返回 message dict。"""

    @abstractmethod
    def chat_stream(self, messages: list, tools=None, temperature: float = 0.7) -> Iterator[dict]:
        """
        流式调用，yield 统一事件：
        - {"type": "content", "delta": "..."}
        - {"type": "tool_calls", "tool_calls": [...], "content": "..."}
        - {"type": "finish", "content": "..."}
        """

    def to_dict(self) -> dict:
        return {
            "id": self.model_id,
            "name": self.display_name,
            "available": self.is_available(),
        }
