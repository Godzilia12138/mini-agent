<template>
  <main class="main">
    <header class="topbar">
      <div class="topbar-left">
        <h1 class="topbar-title">{{ title }}</h1>
      </div>
      <div class="topbar-actions">
        <ModelSelector
          :models="models"
          :model-value="currentModel"
          :disabled="loading"
          @change="$emit('model-change', $event)"
        />
        <ThinkingToggle
          :model-value="thinking"
          :disabled="loading"
          @change="$emit('thinking-change', $event)"
        />
      </div>
    </header>

    <MessageList
      :messages="messages"
      :loading="loading"
      @quick="$emit('quick', $event)"
    />

    <!-- 重试/断连提示 -->
    <div v-if="retryStatus" class="retry-bar">
      <div class="retry-spinner"></div>
      <span>{{ retryStatus }}</span>
    </div>

    <ChatComposer
      :model-value="input"
      :file="file"
      :loading="loading"
      :can-send="canSend"
      @update:model-value="$emit('update:input', $event)"
      @send="$emit('send')"
      @stop="$emit('stop')"
      @file-selected="$emit('file-selected', $event)"
      @remove-file="$emit('remove-file')"
    />
  </main>
</template>

<script>
import MessageList from "./MessageList.vue";
import ChatComposer from "./ChatComposer.vue";
import ModelSelector from "./ModelSelector.vue";
import ThinkingToggle from "./ThinkingToggle.vue";

export default {
  components: { MessageList, ChatComposer, ModelSelector, ThinkingToggle },
  props: {
    title: { type: String, default: "Mini AI Agent" },
    messages: { type: Array, default: () => [] },
    input: { type: String, default: "" },
    file: { type: Object, default: null },
    loading: { type: Boolean, default: false },
    canSend: { type: Boolean, default: false },
    models: { type: Array, default: () => [] },
    currentModel: { type: String, default: "" },
    thinking: { type: Boolean, default: false },
    retryStatus: { type: String, default: "" },
  },
  emits: [
    "update:input", "send", "stop", "quick",
    "file-selected", "remove-file", "model-change", "thinking-change",
  ],
};
</script>

<style scoped>
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: linear-gradient(180deg, #08080e 0%, #0c0c18 100%);
  position: relative;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(8, 8, 14, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 10;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.topbar-title {
  font-size: 14px;
  font-weight: 600;
  color: #e4e4e7;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.2px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* ── Retry bar ── */
.retry-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 8px 16px;
  margin: 0 24px 8px;
  border-radius: 10px;
  background: rgba(251, 146, 60, 0.1);
  border: 1px solid rgba(251, 146, 60, 0.2);
  font-size: 12px;
  color: #fb923c;
  animation: fadeSlideIn 0.3s ease;
}

.retry-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(251, 146, 60, 0.3);
  border-top-color: #fb923c;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
