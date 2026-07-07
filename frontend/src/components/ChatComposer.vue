<template>
  <div class="composer">
    <!-- File chip -->
    <div v-if="file" class="file-chip">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
      <span class="file-name">{{ file.name }}</span>
      <span class="file-size">{{ (file.size / 1024).toFixed(1) }} KB</span>
      <button class="chip-remove" @click="$emit('remove-file')" title="移除文件">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <div class="composer-box" :class="{ 'has-file': file }">
      <!-- Attach button -->
      <label class="attach-btn" title="上传文件（支持 .txt / .md / .py / .docx）">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
        </svg>
        <input type="file" hidden @change="onFileChange" accept=".txt,.md,.py,.js,.ts,.jsx,.tsx,.json,.csv,.xml,.yaml,.yml,.docx,.pdf" />
      </label>

      <!-- Input -->
      <textarea
        ref="inputEl"
        :value="modelValue"
        placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
        rows="1"
        @input="onInput"
        @keydown="onKeydown"
        :disabled="loading"
      ></textarea>

      <!-- Action buttons -->
      <div class="composer-actions">
        <button v-if="loading" class="btn-action btn-stop" @click="$emit('stop')" title="停止">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="1.5"/>
          </svg>
        </button>
        <button
          v-else
          class="btn-action btn-send"
          :disabled="!canSend"
          @click="$emit('send')"
          title="发送"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    modelValue: { type: String, default: "" },
    file: { type: Object, default: null },
    loading: { type: Boolean, default: false },
    canSend: { type: Boolean, default: false },
  },
  emits: ["update:modelValue", "send", "stop", "file-selected", "remove-file"],

  methods: {
    onInput(e) {
      this.$emit("update:modelValue", e.target.value);
      this.autoResize();
    },
    onKeydown(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.$emit("send");
      }
    },
    onFileChange(e) {
      const f = e.target.files[0];
      if (f) this.$emit("file-selected", f);
      e.target.value = "";
    },
    autoResize() {
      this.$nextTick(() => {
        const el = this.$refs.inputEl;
        if (!el) return;
        el.style.height = "auto";
        el.style.height = Math.min(el.scrollHeight, 180) + "px";
      });
    },
  },
};
</script>

<style scoped>
.composer {
  padding: 8px 24px 16px;
}

/* ── File chip ── */
.file-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px 6px 8px;
  margin-bottom: 8px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.18);
  border-radius: 8px;
  font-size: 12px;
  color: #a5b4fc;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.file-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 10px;
  color: #63636b;
  margin-right: 2px;
}

.chip-remove {
  background: none;
  border: none;
  color: #52525b;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: all 0.15s;
}
.chip-remove:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

/* ── Composer box ── */
.composer-box {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 10px 10px 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  transition: all 0.2s;
}
.composer-box:focus-within {
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.06), 0 0 20px rgba(99, 102, 241, 0.04);
}

.attach-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: #52525b;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
  margin-bottom: 2px;
}
.attach-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #a1a1aa;
}

.composer-box textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: #e4e4e7;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.6;
  resize: none;
  outline: none;
  max-height: 180px;
  padding: 4px 0;
}
.composer-box textarea::placeholder {
  color: #3f3f46;
}

.composer-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.btn-action {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}

.btn-send {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}
.btn-send:hover:not(:disabled) {
  opacity: 0.9;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
.btn-send:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}

.btn-stop {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
.btn-stop:hover {
  background: rgba(239, 68, 68, 0.2);
}
</style>
