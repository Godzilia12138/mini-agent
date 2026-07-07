<template>
  <aside class="sidebar">
    <div class="sidebar-top">
      <div class="brand">
        <div class="brand-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="brand-name">Mini Agent</span>
        <span class="brand-ver">v0.2</span>
      </div>

      <button class="btn-new" @click="$emit('new-chat')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        新建对话
      </button>
    </div>

    <div class="chat-list">
      <div
        v-for="chat in chatList"
        :key="chat.id"
        class="chat-item"
        :class="{ active: currentChatId === chat.id }"
        @click="$emit('switch-chat', chat.id)"
      >
        <svg class="chat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span class="chat-title">{{ chat.title }}</span>
        <button
          v-if="chatList.length > 1"
          class="btn-delete"
          @click.stop="$emit('delete-chat', chat.id)"
          title="删除"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="status-dot" :class="apiStatus"></div>
      <span class="status-text">{{ statusText }}</span>
    </div>
  </aside>
</template>

<script>
export default {
  props: {
    chatList: { type: Array, required: true },
    currentChatId: { type: [Number, String], default: null },
    apiStatus: { type: String, default: "checking" },
    statusText: { type: String, default: "" },
  },
  emits: ["new-chat", "switch-chat", "delete-chat"],
};
</script>

<style scoped>
.sidebar {
  width: 270px;
  background: #0c0c14;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-top {
  padding: 18px 14px 10px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.brand-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.brand-name {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: #f4f4f5;
}

.brand-ver {
  font-size: 10px;
  color: #52525b;
  font-weight: 500;
  margin-left: auto;
}

.btn-new {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  border-radius: 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-new:hover {
  background: rgba(99, 102, 241, 0.18);
  border-color: rgba(99, 102, 241, 0.35);
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 2px 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #a1a1aa;
  transition: all 0.15s;
  margin-bottom: 1px;
}
.chat-item:hover {
  background: rgba(255, 255, 255, 0.04);
  color: #e4e4e7;
}
.chat-item.active {
  background: rgba(99, 102, 241, 0.1);
  color: #c7d2fe;
}

.chat-icon {
  flex-shrink: 0;
  opacity: 0.4;
}
.chat-item.active .chat-icon {
  opacity: 0.7;
}

.chat-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-delete {
  background: none;
  border: none;
  color: #52525b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chat-item:hover .btn-delete {
  opacity: 1;
}
.btn-delete:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.sidebar-footer {
  padding: 12px 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #52525b;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.online {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.4);
}
.status-dot.offline {
  background: #ef4444;
}
.status-dot.error {
  background: #f59e0b;
}
.status-dot.checking {
  background: #52525b;
  animation: pulse 1.5s infinite;
}

.status-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
