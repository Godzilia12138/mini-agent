<template>
  <div
    ref="container"
    class="markdown-body"
    :class="{ streaming }"
    v-html="html"
    @click="handleCopy"
  ></div>
</template>

<script>
import { renderMarkdown } from "../utils/markdown.js";

export default {
  props: {
    content: { type: String, default: "" },
    streaming: { type: Boolean, default: false },
  },

  data() {
    return { html: "", timer: null };
  },

  watch: {
    content: {
      immediate: true,
      handler(val) {
        if (this.streaming) {
          clearTimeout(this.timer);
          this.timer = setTimeout(() => this.updateHtml(val), 80);
        } else {
          clearTimeout(this.timer);
          this.updateHtml(val);
        }
      },
    },
    streaming(val) {
      if (!val) this.updateHtml(this.content);
    },
  },

  beforeUnmount() {
    clearTimeout(this.timer);
  },

  methods: {
    updateHtml(text) {
      this.html = renderMarkdown(text);
    },

    async handleCopy(e) {
      const btn = e.target.closest(".copy-code-btn");
      if (!btn) return;
      const code = decodeURIComponent(btn.dataset.code || "");
      try {
        await navigator.clipboard.writeText(code);
        btn.textContent = "已复制 ✓";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = "复制";
          btn.classList.remove("copied");
        }, 2000);
      } catch {
        btn.textContent = "复制失败";
      }
    },
  },
};
</script>

<style scoped>
.markdown-body {
  font-size: 14px;
  line-height: 1.7;
  color: #d4d4d8;
  word-break: break-word;
}
.markdown-body.streaming :deep(pre) {
  opacity: 0.85;
}
.markdown-body :deep(p) { margin-bottom: 8px; }
.markdown-body :deep(p:last-child) { margin-bottom: 0; }
.markdown-body :deep(code) {
  background: rgba(255,255,255,0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: Consolas, monospace;
}
.markdown-body :deep(.code-block-wrapper) {
  margin: 12px 0;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.08);
  background: #0d0d14;
}
.markdown-body :deep(.code-block-header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: rgba(255,255,255,0.04);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.markdown-body :deep(.code-lang) {
  font-size: 11px;
  color: #71717a;
  text-transform: lowercase;
}
.markdown-body :deep(.copy-code-btn) {
  background: rgba(99,102,241,0.15);
  border: 1px solid rgba(99,102,241,0.3);
  color: #a5b4fc;
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}
.markdown-body :deep(.copy-code-btn:hover) {
  background: rgba(99,102,241,0.25);
}
.markdown-body :deep(.copy-code-btn.copied) {
  background: rgba(34,197,94,0.15);
  border-color: rgba(34,197,94,0.3);
  color: #4ade80;
}
.markdown-body :deep(pre) {
  margin: 0;
  padding: 14px 16px;
  overflow-x: auto;
  background: #0d0d14;
}
.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 13px;
  font-family: Consolas, monospace;
}
.markdown-body :deep(ul), .markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) {
  color: #f4f4f5;
  margin: 12px 0 6px;
}
.markdown-body :deep(blockquote) {
  border-left: 3px solid #6366f1;
  padding-left: 12px;
  color: #a1a1aa;
  margin: 8px 0;
}
.markdown-body :deep(a) { color: #818cf8; }
</style>
