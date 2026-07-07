"""原生思考模式：通过各厂商 API 参数开启，非 prompt 模拟。"""

from app.tools import tool_registry


def parse_thinking(value) -> bool:
    """解析 thinking 参数（Form / JSON / 旧 mode 兼容）。"""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in ("1", "true", "yes", "on", "think", "deep"):
        return True
    if s in ("0", "false", "no", "off", "normal", ""):
        return False
    return False


def supports_native_thinking(provider_name: str, model_name: str) -> bool:
    """当前模型是否支持原生思考 API。"""
    m = model_name.lower()
    if provider_name == "deepseek":
        return True
    if provider_name == "qwen":
        return True
    if provider_name == "kimi":
        return m.startswith("kimi-k2") or "thinking" in m
    if provider_name == "glm":
        return "glm-4" in m
    return False


def apply_thinking_payload(payload: dict, provider_name: str, model_name: str, thinking: bool) -> dict:
    """按厂商写入原生思考开关参数。"""
    if not thinking:
        # 混合思考模型：显式关闭
        if provider_name == "deepseek":
            payload["thinking"] = {"type": "disabled"}
        elif provider_name in ("qwen", "kimi", "glm"):
            payload["enable_thinking"] = False
        return payload

    if provider_name == "deepseek":
        payload["thinking"] = {"type": "enabled"}
    elif provider_name in ("qwen", "kimi", "glm"):
        payload["enable_thinking"] = True
    return payload


def build_system_prompt() -> str:
    """统一 system prompt（思考由模型原生能力完成，不再靠 prompt 模拟）。"""
    tool_lines = "\n".join(f"- {t['name']}：{t['description']}" for t in tool_registry.list_tools())
    return f"""你是一个智能 AI 助手，具备文件读取、计算和数据库查询能力。

你可以使用以下工具：
{tool_lines}

工作方式：
1. 当用户询问文件、数据或计算问题时，先调用合适的工具获取信息
2. 基于工具返回的真实数据给出清晰、有条理的回答
3. 回答使用 Markdown 格式，代码块用 ``` 包裹
4. 不要编造工具未返回的内容
5. 语气自然友好，避免机械重复用户问题"""
