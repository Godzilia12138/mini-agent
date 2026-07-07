import json
import re

from app.router import model_router
from app.memory import Memory
from app.tools import tool_registry
from app.thinking import build_system_prompt, parse_thinking, supports_native_thinking

# ── 上下文窗口管理 ──
MAX_CONTEXT_CHARS = 12000      # 超过此字符数触发滑动窗口
KEEP_RECENT_MSGS = 4           # 至少保留最近 N 轮对话
MAX_TOOL_RESULT_CHARS = 4000   # 工具返回结果最大字符数
SUMMARIZE_AFTER = 20           # 超过 N 条消息时做摘要压缩


def _estimate_tokens(text: str) -> int:
    """粗略估算 token 数（中英文混排）。"""
    if not text:
        return 0
    cn = len(re.findall(r'[一-鿿㐀-䶿豈-﫿]', text))
    en = len(re.findall(r'[a-zA-Z0-9]', text))
    return cn * 2 + en // 2 + len(text.split()) // 2


def _trim_context(messages: list[dict]) -> list[dict]:
    """截断过长的对话历史，保留最近的对话和 system prompt。"""
    if not messages:
        return messages

    system_msgs = [m for m in messages if m.get("role") == "system"]
    history = [m for m in messages if m.get("role") != "system"]

    total = sum(_estimate_tokens(json.dumps(m, ensure_ascii=False)) for m in messages)
    if total <= MAX_CONTEXT_CHARS:
        return messages

    # 保留最近的 KEEP_RECENT_MSGS 轮
    keep = min(KEEP_RECENT_MSGS * 2, len(history))
    recent = history[-keep:] if keep > 0 else history
    truncated = system_msgs + recent

    # 如果还是太长，从中间丢弃（保留首尾）
    if sum(_estimate_tokens(json.dumps(m, ensure_ascii=False)) for m in truncated) > MAX_CONTEXT_CHARS and len(truncated) > 4:
        # 保留 system + 第1轮 + 最后2轮
        first_round = truncated[len(system_msgs):len(system_msgs)+2] if len(truncated) > len(system_msgs) + 2 else []
        keep_recent = truncated[-4:] if len(truncated) >= 4 else truncated[len(system_msgs):]
        truncated = system_msgs + first_round + keep_recent

    return truncated


class Agent:

    def __init__(self, session_id: str = "", title: str = "新对话", model: str | None = None):
        self.session_id = session_id
        self.title = title
        self.model = model_router.resolve_model_id(model)
        self.memory = Memory()

    def load_from_store(self, data: dict):
        self.title = data.get("title", "新对话")
        self.model = model_router.resolve_model_id(data.get("model"))
        self.memory.chat = data.get("messages", [])
        self.memory.files = data.get("files", {})

    def to_store(self) -> dict:
        return {
            "title": self.title,
            "model": self.model,
            "messages": self.memory.chat,
            "files": self.memory.files,
        }

    def set_model(self, model_id: str):
        self.model = model_router.resolve_model_id(model_id)
        provider = model_router.get_provider(self.model)
        if not provider.is_available():
            raise ValueError(f"模型 {provider.display_name} 未配置 API Key")

    def _get_provider(self):
        provider = model_router.get_provider(self.model)
        if not provider.is_available():
            raise ValueError(f"模型 {provider.display_name} 未配置 API Key，请在 .env 中配置")
        return provider

    def _build_messages(self):
        messages = [{"role": "system", "content": build_system_prompt()}]

        for msg in self.memory.chat:
            messages.append({"role": msg["role"], "content": msg["content"]})

        if self.memory.files:
            file_summary = "\n\n".join(
                f"📄 **{name}**（已上传，共 {len(content)} 字符）\n{content[:3000]}"
                + ("..." if len(content) > 3000 else "")
                for name, content in self.memory.files.items()
            )
            messages.append({
                "role": "system",
                "content": f"用户已上传以下文件，可直接参考：\n\n{file_summary}",
            })

        # 上下文窗口管理：截断过长历史
        messages = _trim_context(messages)
        return messages

    def _execute_tool(self, name: str, arguments: str):
        try:
            args = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError:
            args = {}
        result = tool_registry.execute(name, args)
        if len(result) > MAX_TOOL_RESULT_CHARS:
            result = result[:MAX_TOOL_RESULT_CHARS] + f"\n\n...（结果过长，已截断至 {MAX_TOOL_RESULT_CHARS} 字符）"
        return result

    def _maybe_update_title(self, task: str):
        if self.title == "新对话" and task.strip():
            self.title = task.strip()[:24] + ("..." if len(task.strip()) > 24 else "")

    def run_stream(self, task: str, thinking: bool = False):
        thinking = parse_thinking(thinking)
        provider = self._get_provider()
        native = thinking and getattr(provider, "supports_thinking", lambda: False)()

        if thinking and not native:
            yield {
                "type": "status",
                "content": "⚠️ 当前模型不支持原生思考，已按普通模式回答",
            }
            thinking = False
            native = False

        self._maybe_update_title(task)
        self.memory.add_chat("user", task)
        messages = self._build_messages()
        tools = tool_registry.get_definitions()
        max_steps = 8 if native else 6

        for _ in range(max_steps):
            tool_calls = None
            content = ""
            reasoning = ""

            for event in provider.chat_stream(messages, tools=tools, thinking=native):
                if event["type"] == "thinking":
                    reasoning += event["delta"]
                    yield {"type": "thinking", "content": event["delta"]}
                elif event["type"] == "content":
                    content += event["delta"]
                    yield {"type": "token", "content": event["delta"]}
                elif event["type"] == "tool_calls":
                    tool_calls = event["tool_calls"]
                    content = event.get("content", content)
                    reasoning = event.get("reasoning_content", reasoning)
                elif event["type"] == "finish":
                    content = event.get("content", content)
                    reasoning = event.get("reasoning_content", reasoning)

            if tool_calls:
                if content.strip() or reasoning.strip():
                    yield {"type": "reset"}
                assistant_msg = {
                    "role": "assistant",
                    "content": content or None,
                    "tool_calls": [
                        {"id": tc["id"], "type": "function", "function": tc["function"]}
                        for tc in tool_calls
                    ],
                }
                if reasoning and native:
                    assistant_msg["reasoning_content"] = reasoning
                messages.append(assistant_msg)

                for call in tool_calls:
                    name = call["function"]["name"]
                    yield {"type": "status", "content": f"🔧 正在调用 {name}..."}
                    result = self._execute_tool(name, call["function"].get("arguments", "{}"))
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": result,
                    })
                continue

            answer = content or "抱歉，我暂时无法回答这个问题。"
            self.memory.add_chat("assistant", answer)
            yield {
                "type": "done",
                "content": answer,
                "thinking": reasoning if native else "",
                "title": self.title,
                "model": self.model,
                "thinking_enabled": native,
            }
            return

        answer = "分析步骤过多，请尝试更具体的问题。"
        self.memory.add_chat("assistant", answer)
        yield {
            "type": "done",
            "content": answer,
            "thinking": "",
            "title": self.title,
            "model": self.model,
            "thinking_enabled": native,
        }
