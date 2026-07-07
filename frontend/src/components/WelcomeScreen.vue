<template>
  <div class="welcome">
    <div class="welcome-glow"></div>
    <div class="welcome-icon">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="url(#grad2)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <defs>
          <linearGradient id="grad2" x1="2" y1="2" x2="22" y2="22">
            <stop offset="0%" stop-color="#818cf8"/>
            <stop offset="100%" stop-color="#a78bfa"/>
          </linearGradient>
        </defs>
      </svg>
    </div>
    <h2 class="welcome-title">有什么可以帮你的？</h2>
    <p class="welcome-sub">我可以读取和分析文件，帮你解答问题</p>
    <div class="quick-actions">
      <button v-for="q in questions" :key="q" @click="$emit('quick', q)">
        <span>{{ q }}</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  emits: ["quick"],
  data() {
    return {
      questions: [
        "列出 workspace 中的文件",
        "帮我分析上传的文件",
        "解释一下 Python 装饰器",
      ],
    };
  },
};
</script>

<style scoped>
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
}

.welcome-glow {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.06) 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.welcome-icon {
  width: 72px;
  height: 72px;
  border-radius: 22px;
  background: rgba(99, 102, 241, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  position: relative;
}

.welcome-title {
  font-size: 22px;
  font-weight: 600;
  color: #f4f4f5;
  letter-spacing: -0.3px;
}

.welcome-sub {
  font-size: 14px;
  color: #52525b;
  margin-bottom: 20px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  max-width: 480px;
}

.quick-actions button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  color: #a1a1aa;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-actions button:hover {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.25);
  color: #c7d2fe;
}

.quick-actions button svg {
  opacity: 0;
  transition: all 0.2s;
}
.quick-actions button:hover svg {
  opacity: 0.6;
  transform: translateX(2px);
}
</style>
