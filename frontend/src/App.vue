<template>
  <div class="app">
    <Sidebar
      :chat-list="chatList"
      :current-chat-id="currentChatId"
      :api-status="apiStatus"
      :status-text="statusText"
      @new-chat="newChat"
      @switch-chat="switchChat"
      @delete-chat="deleteChat"
    />

    <ChatPanel
      :title="currentChat?.title || 'Mini AI Agent'"
      :messages="currentMessages"
      :input="input"
      :file="file"
      :loading="loading"
      :can-send="canSend"
      :models="models"
      :current-model="currentModel"
      :thinking="currentThinking"
      :retry-status="retryStatus"
      @update:input="input = $event"
      @send="sendMessage"
      @stop="stopRequest"
      @quick="sendQuick"
      @file-selected="handleFile"
      @remove-file="file = null"
      @model-change="onModelChange"
      @thinking-change="onThinkingChange"
    />
  </div>
</template>

<script>
import Sidebar from "./components/Sidebar.vue";
import ChatPanel from "./components/ChatPanel.vue";
import {
  checkHealth,
  fetchModels,
  fetchSessions,
  fetchSession,
  createSession,
  deleteSession,
  updateSessionModel,
  streamChat,
} from "./api/chat.js";

export default {
  components: { Sidebar, ChatPanel },

  data() {
    return {
      input: "",
      chatList: [],
      currentChatId: null,
      file: null,
      loading: false,
      controller: null,
      apiStatus: "checking",
      statusText: "检查连接...",
      models: [],
      defaultModel: "deepseek-v4-flash",
      retryStatus: "",
    };
  },

  computed: {
    currentChat() {
      return this.chatList.find(c => c.id === this.currentChatId);
    },
    currentMessages() {
      return this.currentChat?.messages || [];
    },
    currentModel() {
      return this.currentChat?.model || this.defaultModel;
    },
    currentModelName() {
      const m = this.models.find(x => x.id === this.currentModel);
      return m?.name || this.currentModel;
    },
    currentThinking() {
      return !!this.currentChat?.thinking;
    },
    canSend() {
      return (this.input.trim() || this.file) && !this.loading;
    },
  },

  mounted() {
    this.init();
  },

  methods: {
    async init() {
      await Promise.all([this.loadModels(), this.checkHealth()]);
      try {
        const { sessions } = await fetchSessions();
        if (sessions.length) {
          this.chatList = sessions.map(s => ({
            id: s.id,
            title: s.title,
            model: s.model || this.defaultModel,
            thinking: false,
            messages: [],
          }));
          this.currentChatId = this.chatList[0].id;
          await this.loadSessionMessages(this.currentChatId);
        } else {
          await this.newChat();
        }
      } catch {
        await this.newChat();
      }
    },

    async loadModels() {
      try {
        const data = await fetchModels();
        this.models = data.models || [];
        this.defaultModel = data.default || data.env_model || "deepseek-v4-flash";
        const available = new Set(this.models.filter(m => m.available).map(m => m.id));
        if (this.currentChat && (!this.currentChat.model || !available.has(this.currentChat.model))) {
          this.currentChat.model = this.defaultModel;
        }
        this.updateStatusText();
      } catch {
        this.models = [];
      }
    },

    async loadSessionMessages(sessionId) {
      try {
        const data = await fetchSession(sessionId);
        const chat = this.chatList.find(c => c.id === sessionId);
        if (chat) {
          chat.title = data.title;
          chat.model = data.model || this.defaultModel;
          chat.messages = (data.messages || []).map(m => ({
            role: m.role,
            content: m.content,
          }));
        }
      } catch {
        /* session may not exist yet on backend */
      }
    },

    async checkHealth() {
      try {
        const data = await checkHealth();
        if (data.api_configured) {
          this.apiStatus = "online";
          this.updateStatusText();
        } else {
          this.apiStatus = "error";
          this.statusText = "API Key 未配置";
        }
      } catch {
        this.apiStatus = "offline";
        this.statusText = "后端未启动";
      }
    },

    async newChat() {
      const id = String(Date.now());
      const model = this.defaultModel;
      this.chatList.unshift({ id, title: "新对话", model, thinking: false, messages: [] });
      this.currentChatId = id;
      try {
        await createSession(id, "新对话", model);
      } catch {
        /* backend may be offline */
      }
    },

    async switchChat(id) {
      this.currentChatId = id;
      const chat = this.chatList.find(c => c.id === id);
      if (chat && !chat.messages.length) {
        await this.loadSessionMessages(id);
      }
    },

    async deleteChat(id) {
      try {
        await deleteSession(id);
      } catch {
        /* ignore */
      }
      this.chatList = this.chatList.filter(c => c.id !== id);
      if (this.currentChatId === id) {
        if (this.chatList.length) {
          this.currentChatId = this.chatList[0].id;
          await this.loadSessionMessages(this.currentChatId);
        } else {
          await this.newChat();
        }
      }
    },

    updateStatusText() {
      if (this.apiStatus === "online") {
        const think = this.currentThinking ? " · 思考开" : "";
        this.statusText = `已连接 · ${this.currentModelName}${think}`;
      }
    },

    async onModelChange(modelId) {
      const chat = this.currentChat;
      if (!chat) return;
      const prev = chat.model;
      chat.model = modelId;
      this.updateStatusText();
      try {
        await updateSessionModel(chat.id, modelId);
      } catch (e) {
        alert(e.message || "切换模型失败");
        chat.model = prev;
        this.updateStatusText();
      }
    },

    onThinkingChange(enabled) {
      const chat = this.currentChat;
      if (!chat) return;
      chat.thinking = enabled;
      this.updateStatusText();
    },

    handleFile(f) {
      this.file = f;
      if (!this.currentChat) this.newChat();
    },

    sendQuick(text) {
      this.input = text;
      this.sendMessage();
    },

    async sendMessage() {
      if (!this.canSend) return;
      if (!this.currentChat) await this.newChat();

      const chat = this.currentChat;
      const text = this.input.trim();
      this.input = "";
      this.retryStatus = "";

      if (this.file) {
        chat.messages.push({
          role: "user",
          content: `📎 ${this.file.name}`,
          isFile: true,
        });
      }
      if (text) {
        chat.messages.push({ role: "user", content: text });
        if (chat.title === "新对话") {
          chat.title = text.slice(0, 24) + (text.length > 24 ? "..." : "");
        }
      }

      const form = new FormData();
      form.append("message", text || "");
      form.append("session_id", String(this.currentChatId));
      form.append("model", chat.model || this.defaultModel);
      form.append("thinking", chat.thinking ? "true" : "false");
      if (this.file) {
        form.append("file", this.file);
        this.file = null;
      }

      chat.messages.push({
        role: "assistant",
        content: "",
        thinking: "",
        showThinking: true,
        streaming: true,
        status: "",
      });
      const msgIdx = chat.messages.length - 1;

      this.loading = true;
      this.controller = new AbortController();

      const patchMsg = (patch) => {
        chat.messages[msgIdx] = { ...chat.messages[msgIdx], ...patch };
      };

      await streamChat(
        form,
        {
          onThinking: (chunk) => {
            const m = chat.messages[msgIdx];
            patchMsg({ thinking: (m.thinking || "") + chunk });
          },
          onToken: (chunk) => {
            const m = chat.messages[msgIdx];
            patchMsg({ content: m.content + chunk });
          },
          onStatus: (status) => {
            // Show retry/reconnect status
            if (status.includes("重试")) {
              this.retryStatus = status;
            }
            patchMsg({ status });
          },
          onReset: () => {
            patchMsg({ content: "", thinking: "" });
          },
          onDone: (data) => {
            patchMsg({
              content: data.content,
              thinking: data.thinking || chat.messages[msgIdx].thinking || "",
              streaming: false,
              status: "",
            });
            if (data.title) chat.title = data.title;
            if (data.model) chat.model = data.model;
            this.retryStatus = "";
          },
          onError: (err) => {
            patchMsg({
              content: err,
              streaming: false,
              status: "",
            });
          },
        },
        this.controller.signal,
      );

      const final = chat.messages[msgIdx];
      if (final?.streaming) {
        patchMsg({
          streaming: false,
          content: final.content || "（无响应，请重试）",
        });
      }

      this.loading = false;
      this.retryStatus = "";
    },

    stopRequest() {
      this.controller?.abort();
      this.loading = false;
      this.retryStatus = "";
      const last = this.currentMessages[this.currentMessages.length - 1];
      if (last?.streaming) {
        last.streaming = false;
        if (!last.content) last.content = "（已停止）";
      }
    },
  },
};
</script>

<style scoped>
.app {
  display: flex;
  height: 100vh;
  background: #08080e;
  color: #e4e4e7;
}
</style>
