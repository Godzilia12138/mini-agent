import json
import time

import requests

from app.config import provider_credentials
from app.providers.base import BaseModelProvider
from app.thinking import apply_thinking_payload, supports_native_thinking

_RETRYABLE_STATUS = {429, 502, 503, 504}
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 2.0


def _iter_sse_lines(response: requests.Response):
    """按 UTF-8 解析 SSE 行，避免 Windows 下 decode_unicode 乱码。"""
    response.encoding = "utf-8"
    for raw in response.iter_lines(decode_unicode=False):
        if not raw:
            continue
        yield raw.decode("utf-8")


class OpenAICompatibleProvider(BaseModelProvider):
    """OpenAI 兼容 API（DeepSeek / Qwen / Kimi / GLM 等）。"""

    def __init__(
        self,
        model_id: str,
        model_name: str,
        display_name: str,
        provider_name: str,
    ):
        self.model_id = model_id
        self.model_name = model_name
        self.display_name = display_name
        self.provider_name = provider_name

    @property
    def api_key(self) -> str:
        return provider_credentials(self.provider_name)[0]

    @property
    def base_url(self) -> str:
        return provider_credentials(self.provider_name)[1].rstrip("/")

    def is_available(self) -> bool:
        key = self.api_key
        return bool(key and key != "YOUR_API_KEY")

    def supports_thinking(self) -> bool:
        return supports_native_thinking(self.provider_name, self.model_name)

    def _effective_temperature(self, temperature: float) -> float:
        if self.provider_name == "kimi" and self.model_name.startswith("kimi-k2"):
            return 1.0
        return temperature

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _check(self):
        if not self.is_available():
            raise ValueError(f"{self.display_name} 未配置 API Key")

    def _parse_error(self, res: requests.Response) -> str:
        res.encoding = "utf-8"
        detail = res.text
        try:
            detail = res.json().get("error", {}).get("message", detail)
        except Exception:
            pass
        return detail

    def _format_api_error(self, res: requests.Response) -> str:
        detail = self._parse_error(res)
        code = res.status_code
        if code == 429:
            return (
                f"{self.display_name} 服务繁忙（429），已自动重试仍失败。"
                f"请稍后再试，或切换到 DeepSeek / Qwen / GLM。详情：{detail}"
            )
        if code in (502, 503, 504):
            return (
                f"{self.display_name} 暂时不可用（{code}），请稍后重试或换模型。详情：{detail}"
            )
        return f"{self.display_name} API 错误 ({code}): {detail}"

    def _retry_delay(self, res: requests.Response, attempt: int) -> float:
        retry_after = res.headers.get("Retry-After")
        if retry_after:
            try:
                return max(_RETRY_BASE_DELAY, float(retry_after))
            except ValueError:
                pass
        return _RETRY_BASE_DELAY * (2 ** attempt)

    def _post_with_retry(self, url: str, *, payload: dict, stream: bool = False):
        last_res = None
        for attempt in range(_MAX_RETRIES + 1):
            res = requests.post(
                url,
                json=payload,
                headers=self._headers(),
                stream=stream,
                timeout=120,
            )
            if res.ok or res.status_code not in _RETRYABLE_STATUS:
                return res
            last_res = res
            if attempt < _MAX_RETRIES:
                time.sleep(self._retry_delay(res, attempt))
        return last_res

    def _build_payload(self, messages, tools, temperature, thinking: bool):
        temperature = self._effective_temperature(temperature)
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        apply_thinking_payload(payload, self.provider_name, self.model_name, thinking)
        return payload

    def _parse_stream_delta(self, delta: dict, thinking_enabled: bool):
        """解析流式 delta，区分思考链与正式回答。"""
        events = []
        if thinking_enabled:
            rc = delta.get("reasoning_content")
            if rc:
                events.append({"type": "thinking", "delta": rc})
        if delta.get("content"):
            events.append({"type": "content", "delta": delta["content"]})
        return events

    def chat(self, messages, tools=None, temperature=0.7, thinking: bool = False):
        self._check()
        payload = self._build_payload(messages, tools, temperature, thinking)
        payload["stream"] = False

        res = self._post_with_retry(
            f"{self.base_url}/chat/completions",
            payload=payload,
            stream=False,
        )
        if not res.ok:
            raise RuntimeError(self._format_api_error(res))

        res.encoding = "utf-8"
        return res.json()["choices"][0]["message"]

    def chat_stream(self, messages, tools=None, temperature=0.7, thinking: bool = False):
        self._check()
        payload = self._build_payload(messages, tools, temperature, thinking)
        payload["stream"] = True

        res = self._post_with_retry(
            f"{self.base_url}/chat/completions",
            payload=payload,
            stream=True,
        )
        if not res.ok:
            raise RuntimeError(self._format_api_error(res))

        content = ""
        reasoning = ""
        tool_calls: dict[int, dict] = {}

        for line in _iter_sse_lines(res):
            if not line.startswith("data: "):
                continue

            data = line[6:].strip()
            if data == "[DONE]":
                break

            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                continue

            delta = obj.get("choices", [{}])[0].get("delta", {})

            for ev in self._parse_stream_delta(delta, thinking):
                if ev["type"] == "thinking":
                    reasoning += ev["delta"]
                    yield ev
                elif ev["type"] == "content":
                    content += ev["delta"]
                    yield ev

            for tc in delta.get("tool_calls") or []:
                idx = tc.get("index", 0)
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "id": tc.get("id", ""),
                        "function": {"name": "", "arguments": ""},
                    }
                fn = tc.get("function", {})
                if fn.get("name"):
                    tool_calls[idx]["function"]["name"] += fn["name"]
                if fn.get("arguments"):
                    tool_calls[idx]["function"]["arguments"] += fn["arguments"]

        if tool_calls:
            yield {
                "type": "tool_calls",
                "tool_calls": [tool_calls[i] for i in sorted(tool_calls)],
                "content": content,
                "reasoning_content": reasoning,
            }
        else:
            yield {"type": "finish", "content": content, "reasoning_content": reasoning}

    def to_dict(self) -> dict:
        return {
            "id": self.model_id,
            "name": self.display_name,
            "available": self.is_available(),
            "supports_thinking": self.supports_thinking(),
        }
