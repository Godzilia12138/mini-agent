<template>
  <div class="message" :class="[msg.role, { streaming: msg.streaming }]">
    <div class="msg-avatar" :class="msg.role">
      <span v-if="msg.role === 'assistant'">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
      </span>
      <span v-else>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
        </svg>
      </span>
    </div>
    <div class="msg-body">
      <div class="msg-name">{{ msg.role === "assistant" ? "Assistant" : "You" }}</div>

      <!-- File indicator -->
      <div v-if="msg.isFile" class="msg-file">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        <span>{{ msg.content }}</span>
      </div>

      <!-- Plain user text -->
      <div v-else-if="msg.role === 'user'" class="msg-text">{{ msg.content }}</div>

      <!-- Assistant response -->
      <template v-else>
        <!-- Thinking block -->
        <details v-if="msg.thinking" class="msg-thinking" :open="msg.streaming">
          <summary>
            <span class="thinking-icon">🧠</span>
            思考过程
            <span v-if="msg.streaming" class="thinking-dots">
              <span></span><span></span><span></span>
            </span>
          </summary>
          <div class="thinking-body">{{ msg.thinking }}</div>
        </details>

        <!-- Streaming content with cursor -->
        <div v-if="msg.streaming" class="msg-streaming">
          <span>{{ msg.content || "▍" }}</span>
          <span class="cursor">▍</span>
        </div>

        <!-- Rendered markdown -->
        <MarkdownContent v-else :content="msg.content" />
      </template>

      <!-- Tool call status -->
      <div v-if="msg.status && !msg.status.includes('重试')" class="msg-status">
        <span class="status-spinner"></span>
        {{ msg.status }}
      </div>
    </div>
  </div>
</template>

<script>
import MarkdownContent from "./MarkdownContent.vue";

export default {
  components: { MarkdownContent },
  props: {
    msg: { type: Object, required: true },
  },
};
</script>

<style scoped>
.message {
  display: flex;
  gap: 14px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.msg-avatar.assistant {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}
.msg-avatar.user {
  background: rgba(255, 255, 255, 0.06);
  color: #a1a1aa;
}

.msg-body {
  flex: 1;
  min-width: 0;
}

.msg-name {
  font-size: 11px;
  font-weight: 600;
  color: #52525b;
  margin-bottom: 4px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

/* ── Thinking block ── */
.msg-thinking {
  margin-bottom: 10px;
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 10px;
  background: rgba(139, 92, 246, 0.04);
  overflow: hidden;
}
.msg-thinking summary {
  cursor: pointer;
  padding: 8px 12px;
  font-size: 12px;
  color: #a78bfa;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 6px;
}
.msg-thinking summary:hover {
  background: rgba(139, 92, 246, 0.04);
}
.thinking-icon {
  font-size: 14px;
}

.thinking-dots {
  display: inline-flex;
  gap: 3px;
  margin-left: 4px;
}
.thinking-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #a78bfa;
  animation: thinkingBounce 1.4s infinite ease-in-out;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes thinkingBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.thinking-body {
  padding: 0 12px 12px;
  font-size: 13px;
  line-height: 1.6;
  color: #8b8bbf;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 320px;
  overflow-y: auto;
}

/* ── Text content ── */
.msg-text {
  font-size: 14px;
  line-height: 1.7;
  color: #d4d4d8;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg-streaming {
  font-size: 14px;
  line-height: 1.7;
  color: #d4d4d8;
  white-space: pre-wrap;
  word-break: break-word;
}
.msg-streaming .cursor {
  color: #6366f1;
  animation: blink 1s step-end infinite;
  font-weight: 300;
}

@keyframes blink {
  50% { opacity: 0; }
}

/* ── File chip ── */
.msg-file {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 8px;
  color: #a5b4fc;
  font-size: 13px;
}

/* ── Status bar ── */
.msg-status {
  margin-top: 8px;
  font-size: 11px;
  color: #63636b;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.status-spinner {
  width: 10px;
  height: 10px;
  border: 1.5px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
