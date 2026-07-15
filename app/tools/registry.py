from app.tools.base import Tool
from app.logger import get_logger, _sanitize
import time

log = get_logger(__name__)


class ToolRegistry:
    """统一工具注册与执行。"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> "ToolRegistry":
        if tool.name in self._tools:
            raise ValueError(f"工具已注册: {tool.name}")
        self._tools[tool.name] = tool
        log.info("工具注册: %s — %s", tool.name, tool.description)
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
            log.warning("未知工具调用: %s", name)
            return f"未知工具: {name}"
        try:
            t0 = time.time()
            result = str(tool.execute(args))
            elapsed = time.time() - t0
            log.info("工具执行: %s | 耗时=%.2fs | 结果长度=%d",
                     name, elapsed, len(result))
            return result
        except Exception as e:
            elapsed = time.time() - t0
            log.error("工具执行异常: %s | 耗时=%.2fs | err=%s", name, elapsed, e, exc_info=True)
            return f"工具执行失败: {e}"

    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
