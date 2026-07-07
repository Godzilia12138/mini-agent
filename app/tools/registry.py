from app.tools.base import Tool


class ToolRegistry:
    """统一工具注册与执行。"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> "ToolRegistry":
        if tool.name in self._tools:
            raise ValueError(f"工具已注册: {tool.name}")
        self._tools[tool.name] = tool
        return self

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def get_definitions(self) -> list[dict]:
        return [t.to_definition() for t in self._tools.values()]

    def list_tools(self) -> list[dict]:
        return [t.to_info() for t in self._tools.values()]

    def execute(self, name: str, args: dict) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"未知工具: {name}"
        try:
            return str(tool.execute(args))
        except Exception as e:
            return f"工具执行失败: {e}"

    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
