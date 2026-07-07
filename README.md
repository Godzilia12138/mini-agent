<div align="center">
  <br>
  <img src="https://img.shields.io/badge/status-active-success" alt="Status">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/vue-3-brightgreen" alt="Vue 3">
  <br><br>

  <h1>🤖 Mini Agent</h1>
  <p><strong>轻量级 AI Agent 聊天平台</strong></p>
  <p>支持多模型路由 · 工具调用 · RAG 知识库 · SSE 流式输出</p>

  <br>
</div>

---

## ✨ 功能

| 功能 | 说明 |
|------|------|
| 🧠 **多模型切换** | DeepSeek / Qwen / Kimi / GLM / OpenAI 一键切换 |
| 🔧 **工具调用** | 文件读写、计算、数据库查询、RAG 语义检索 |
| 📄 **文件分析** | 上传 .txt / .md / .py / .docx 等文件，自动索引到知识库 |
| 💬 **流式对话** | SSE 实时流式输出，支持中断/重试 |
| 🧩 **MCP 扩展** | 接入 MCP 服务器，扩展工具能力 |
| 🗂️ **多会话** | 创建/切换/删除会话，SQLite 持久化 |

## 🏗️ 架构

```
Vue 3 Frontend
    ↓ SSE (text/event-stream)
FastAPI Gateway
    ↓
Agent Core (tool loop)
    ↓
Model Router ──→ DeepSeek / Qwen / Kimi / GLM
    ↓
Tool System ──→ File / Calculator / DB / RAG / MCP
    ↓
Storage ──→ SQLite + RAG (TF-IDF / FAISS)
```

## 🚀 快速开始

### 前置条件

- Python 3.10+
- Node.js 18+

### 后端

```bash
# 1. 克隆
git clone https://github.com/Godzilia12138/mini-agent.git
cd mini-agent

# 2. 创建虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 5. 启动后端
uvicorn app.server:app --reload --port 8000
```

### 前端

```bash
# 新开一个终端
cd mini-agent/frontend
npm install
npm run dev
```

访问 **http://localhost:5173** 🎉

## ⚙️ 配置

编辑 `.env` 文件：

```env
# 默认模型
MODEL=deepseek-chat

# DeepSeek（至少配一个）
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Qwen（可选）
QWEN_API_KEY=sk-...
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Kimi / GLM 等可选
# 详见 .env.example
```

## 📁 项目结构

```
mini-agent/
├── app/                    # 后端
│   ├── server.py           # FastAPI 路由入口
│   ├── agent.py            # Agent 核心（工具循环）
│   ├── router.py           # 多模型路由
│   ├── providers/          # LLM 提供商适配
│   ├── tools/              # 工具系统
│   ├── rag/                # RAG 知识库
│   ├── mcp/                # MCP 客户端桥接
│   ├── db/                 # SQLite 持久化
│   ├── session.py          # 会话管理
│   ├── thinking.py         # 原生思考链
│   └── config.py           # 环境配置
├── frontend/src/           # Vue 3 前端
│   ├── App.vue
│   ├── api/                # SSE 流式请求
│   ├── components/         # 聊天组件
│   └── utils/              # Markdown 渲染
├── .env.example            # 环境变量模板
└── requirements.txt
```

## 📸 截图

> *（你可以在这里放截图）*

## 🧩 支持的模型

| 提供商 | 模型 | 状态 |
|--------|------|------|
| DeepSeek | deepseek-chat, deepseek-v4-flash | ✅ |
| 阿里云 Qwen | qwen-plus, qwen-turbo, qwen-max | ✅ |
| Moonshot Kimi | moonshot-v1-32k, kimi-k2 | ✅ |
| 智谱 GLM | glm-4-flash, glm-4, glm-4-plus | ✅ |
| OpenAI | gpt-4o-mini | ✅ |

## 📄 开源协议

MIT
