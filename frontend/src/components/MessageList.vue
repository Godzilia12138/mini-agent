<template>
  <div class="messages" ref="container">
    <WelcomeScreen
      v-if="!messages.length && !loading"
      @quick="$emit('quick', $event)"
    />

    <MessageItem
      v-for="(msg, index) in messages"
      :key="index"
      :msg="msg"
    />

    <div v-if="loading && !hasStreamingMsg" class="loading-indicator">
      <div class="loading-bubble">
        <div class="loading-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import WelcomeScreen from "./WelcomeScreen.vue";
import MessageItem from "./MessageItem.vue";

export default {
  components: { WelcomeScreen, MessageItem },
  props: {
    messages: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
  },
  emits: ["quick"],
  computed: {
    hasStreamingMsg() {
      return this.messages.some(m => m.streaming);
    },
  },
  watch: {
    messages: {
      deep: true,
      handler() {
        this.$nextTick(() => this.scrollBottom());
      },
    },
    loading() {
      this.$nextTick(() => this.scrollBottom());
    },
  },
  methods: {
    scrollBottom() {
      this.$nextTick(() => {
        const el = this.$refs.container;
        if (el) {
          el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
        }
      });
    },
  },
};
</script>

<style scoped>
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 8px;
  scroll-behavior: smooth;
}

/* ── Loading indicator ── */
.loading-indicator {
  display: flex;
  padding: 8px 0;
}

.loading-bubble {
  display: inline-flex;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px 16px 16px 4px;
}

.loading-dots {
  display: flex;
  gap: 6px;
  align-items: center;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6366f1;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
.loading-dots span:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
