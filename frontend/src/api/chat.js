const API = "/api";

/** 开发环境直连后端，避免 Vite 代理缓冲 SSE */
const STREAM_URL = import.meta.env.DEV
  ? "http://127.0.0.1:8000/chat/stream"
  : `${API}/chat/stream`;

const MAX_RETRIES = 3;
const RETRY_DELAY = 1500; // ms

export async function checkHealth() {
  const res = await fetch(`${API}/health`);
  if (!res.ok) throw new Error("health check failed");
  return res.json();
}

export async function fetchModels() {
  const res = await fetch(`${API}/models`);
  if (!res.ok) throw new Error("fetch models failed");
  return res.json();
}

export async function updateSessionModel(sessionId, model) {
  const form = new FormData();
  form.append("model", model);
  const res = await fetch(`${API}/sessions/${sessionId}/model`, {
    method: "PUT",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "update model failed");
  }
  return res.json();
}

export async function fetchSessions() {
  const res = await fetch(`${API}/sessions`);
  if (!res.ok) throw new Error("fetch sessions failed");
  return res.json();
}

export async function fetchSession(sessionId) {
  const res = await fetch(`${API}/sessions/${sessionId}`);
  if (!res.ok) throw new Error("fetch session failed");
  return res.json();
}

export async function createSession(sessionId, title = "新对话", model = null) {
  const form = new FormData();
  form.append("session_id", String(sessionId));
  form.append("title", title);
  if (model) form.append("model", model);
  const res = await fetch(`${API}/sessions`, { method: "POST", body: form });
  if (res.status === 409) return null;
  if (!res.ok) throw new Error("create session failed");
  return res.json();
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${API}/sessions/${sessionId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("delete session failed");
  return res.json();
}

function parseSSEChunk(raw, callbacks) {
  const { onToken, onThinking, onStatus, onReset, onDone, onError } = callbacks;
  const text = raw.replace(/\r\n/g, "\n").trim();
  if (!text) return;

  for (const line of text.split("\n")) {
    if (!line.startsWith("data:")) continue;
    const payload = line.slice(5).trim();
    if (!payload) continue;
    try {
      const data = JSON.parse(payload);
      switch (data.type) {
        case "thinking":
          onThinking?.(data.content);
          break;
        case "token":
          onToken?.(data.content);
          break;
        case "status":
          onStatus?.(data.content);
          break;
        case "reset":
          onReset?.();
          break;
        case "done":
          onDone?.(data);
          break;
        case "error":
          onError?.(data.content);
          break;
      }
    } catch {
      /* skip malformed */
    }
  }
}

/**
 * Sleep helper
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * SSE 流式聊天（带自动重试）
 */
export async function streamChat(formData, callbacks, signal) {
  let retryCount = 0;

  async function attempt() {
    const res = await fetch(STREAM_URL, {
      method: "POST",
      body: formData,
      signal,
    });

    if (!res.ok) {
      const err = await res.text();
      callbacks.onError?.(`请求失败 (${res.status}): ${err}`);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let lastChunkTime = Date.now();

    while (true) {
      let result;
      try {
        result = await reader.read();
      } catch (e) {
        // AbortError — user cancelled
        if (e.name === "AbortError") return;
        // Read error — retry if possible
        if (retryCount < MAX_RETRIES) {
          retryCount++;
          callbacks.onStatus?.(`⚠️ 连接中断，正在重试 (${retryCount}/${MAX_RETRIES})...`);
          await sleep(RETRY_DELAY * retryCount);
          return attempt();
        }
        callbacks.onError?.(`连接中断，重试 ${MAX_RETRIES} 次后失败`);
        return;
      }

      const { done, value } = result;
      if (done) break;

      lastChunkTime = Date.now();
      buffer += decoder.decode(value, { stream: true });
      buffer = buffer.replace(/\r\n/g, "\n");

      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      for (const part of parts) {
        parseSSEChunk(part, callbacks);
      }
    }

    // 刷新剩余 buffer（最后一个 event 可能没有尾随 \n\n）
    if (buffer.trim()) {
      parseSSEChunk(buffer, callbacks);
    }
  }

  return attempt();
}
