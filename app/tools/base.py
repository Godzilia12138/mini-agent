from abc import ABC, abstractmethod


class Tool(ABC):
    """工具抽象基类。"""

    name: str
    description: str
    parameters: dict

    def to_definition(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    @abstractmethod
    def execute(self, args: dict) -> str:
        pass

    def to_info(self) -> dict:
        return {"name": self.name, "description": self.description}
