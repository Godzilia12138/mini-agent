# Mini Agent — Cursor 项目说明

> **一句话总结**：这是一个基于 FastAPI + Vue 的 AI Agent 聊天平台，当前已完成 SSE 流式对话、工具调用和 JSON 会话持久化；下一阶段目标是升级为支持多模型路由、SQLite/MySQL 数据库、RAG 知识库和可扩展 Tool System 的完整 Agent 平台。

---

## 当前已完成

| 模块 | 状态 | 说明 |
|------|------|------|
| FastAPI 后端 | ✅ | `app/server.py`，端口 8000 |
| Vue 3 前端 | ✅ | `frontend/src/`，Vite 开发端口 5173 |
| SSE 流式接口 | ✅ | `POST /chat/stream` |
| Agent 架构 | ✅ | `app/agent.py` — `run_stream()` + tool calling |
| 会话系统 | ✅ | `GET/POST/DELETE /sessions`，JSON 持久化 |
| Markdown UI | ✅ | highlight.js 代码高亮 + 复制按钮 |
| 文件工具 | ✅ | `list_files` / `search_file` / `read_file` |

---

## 已修复的核心问题

### 问题 1：前端无流式输出

**现象**：点击发送后 loading，后端有响应，但前端消息空白。

**根因**：`app/llm.py` 中 `chat_stream()` 解析层错误 — SSE 与 JSON 混用，`content` 未正确 yield，导致前端 `onToken` 永远不触发。

**修复**：重写 `chat_stream()`，统一事件格式：

```python
{"type": "content", "delta": "..."}   # 文本 token
{"type": "tool_calls", "tool_calls": [...], "content": "..."}
{"type": "finish", "content": "..."}
```

### 问题 2：流式事件链断裂风险

**链路**：

```
DeepSeek API → chat_stream → agent.run_stream → SSE → Vue onToken
```

**风险点**：

- event type 不稳定（`content` / `delta` 混用）
- `tool_calls` 结构复杂，index 累积
- `finish` / `done` 命名不统一（后端 agent 层用 `done`，llm 层用 `finish`）

**当前约定**（必须保持一致）：

| 层级 | 事件类型 | 含义 |
|------|----------|------|
| `llm.chat_stream` | `content` | 文本 delta |
| `llm.chat_stream` | `tool_calls` | 需执行工具 |
| `llm.chat_stream` | `finish` | 流结束，无工具 |
| `agent.run_stream` | `token` | 转发给前端的文本 |
| `agent.run_stream` | `status` | 工具调用状态 |
| `agent.run_stream` | `reset` | 清空前端已输出（工具轮次切换） |
| `agent.run_stream` | `done` | 完成，触发持久化 |
| SSE → 前端 | 同上 | `api/chat.js` 解析 |

---

## 当前系统隐患

1. **模型层与 Agent 强耦合** — `llm.py` 硬编码 DeepSeek，无法切换模型
2. **工具系统不可扩展** — `TOOL_HANDLERS` 写死 dict，无法动态注册
3. **Session 未用数据库** — `data/sessions.json`，重启可恢复但无法并发、无索引
4. **无 RAG 知识库** — 只能读 workspace 文件，无法语义检索
5. **前端无法切换模型** — 模型由 `.env` 的 `MODEL` 决定
6. **所有数据依赖内存 + JSON** — Agent 实例在内存，JSON 仅作持久化快照

---

## 项目结构

```
mini-agent/
├── app/
│   ├── server.py        # FastAPI 路由（/chat/stream, /sessions）
│   ├── agent.py         # Agent.run_stream() + tool loop
│   ├── llm.py           # chat() / chat_stream() — DeepSeek API
│   ├── tools/           # ToolRegistry + 各工具实现
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── file_tools.py
│   │   ├── calculator.py
│   │   └── extended_tools.py
│   ├── session.py       # SessionManager（内存 + JSON 持久化）
│   ├── persistence.py   # data/sessions.json 读写
│   └── memory.py        # 单会话 chat + files 内存
├── frontend/src/
│   ├── App.vue          # 状态编排
│   ├── api/chat.js      # SSE fetch 封装
│   ├── utils/markdown.js
│   └── components/      # Sidebar, ChatPanel, MessageList, ...
├── data/sessions.json   # 会话持久化（JSON）
├── workspace/           # 文件工具工作区
├── .env                 # API_KEY, BASE_URL, MODEL
└── AGENTS.md            # 本文件
```

---

## 启动方式

```powershell
# 终端 1 — 后端
cd F:\mini-agent
.\venv\Scripts\Activate.ps1
uvicorn app.server:app --reload --port 8000

# 终端 2 — 前端
cd F:\mini-agent\frontend
npm run dev
```

访问：`http://localhost:5173`（Vite 代理 `/api` → `8000`）

> ⚠️ 不要用 `python app/main.py`（那是旧 mock 接口）

---

## 下一阶段目标：AI Agent 平台

### 1️⃣ 多模型系统（优先级：P0）✅ 已完成

| 模型 ID | 状态 |
|---------|------|
| `deepseek-chat` | ✅ 需 API_KEY |
| `deepseek-v4-flash` | ✅ 默认模型 |
| `qwen-plus` / `qwen-turbo` | ✅ 需 QWEN_API_KEY |
| `gpt-4o-mini` | ✅ 需 OPENAI_API_KEY |
| `claude-3-5-sonnet` | 🔜 预留 Stub |

**实现**：`app/providers/` + `app/router.py` + `GET /models` + `PUT /sessions/{id}/model` + 前端 `ModelSelector.vue`

---

### 2️⃣ 数据库系统（优先级：P0）✅ 已完成

**实现**：SQLite `data/mini_agent.db`

| 表 | 说明 |
|----|------|
| `sessions` | id, title, model, created_at, updated_at |
| `messages` | session_id, role, content, created_at |
| `files` | session_id, filename, content, created_at |

**文件**：
- `app/db/database.py` — 连接与 schema
- `app/db/repository.py` — SessionRepository
- `app/persistence.py` — 统一持久化接口

**API 方法**：`save_message()` / `load_messages()` / `save_file()`

**迁移**：首次启动自动从 `data/sessions.json` 迁移，原文件备份为 `sessions.json.bak`

---

### 3️⃣ RAG 知识库（优先级：P1）✅ 已完成

**流程**：文件上传 → 分块 → 向量化 → 检索 → `rag_search` 工具

**实现**：
```
app/rag/
├── chunker.py    # 文本分块
├── embedder.py   # TF-IDF / API / 本地 embedding
├── store.py      # 向量存储（默认 TF-IDF）
├── indexer.py    # 索引入口
├── retriever.py  # 检索格式化
└── service.py    # rag_service 单例
```

**工具**：`rag_search` / `rag_index` / `rag_status`

**API**：
- `GET /rag/status` — 知识库状态
- `GET /rag/search?q=...` — 调试检索
- `POST /rag/index` — 手动索引 workspace 文件

**配置**（`.env`）：
```env
RAG_EMBEDDING_MODE=tfidf   # tfidf（默认，无需下载）| api | local
# EMBEDDING_API_KEY=      # api 模式
# RAG_EMBEDDING_MODEL=    # local 模式
```

上传文件会自动索引到 `data/rag/`。

---

### 4️⃣ Tool System 重构（优先级：P1）✅ 已完成

**实现**：

```python
# app/tools/base.py      → Tool 抽象基类
# app/tools/registry.py  → ToolRegistry（register / execute / get_definitions）
# app/tools/file_tools.py
# app/tools/calculator.py
# app/tools/extended_tools.py  → db_query / rag_search / web_search
```

| 工具 | 状态 |
|------|------|
| `list_files` / `search_file` / `read_file` / `write_file` | ✅ |
| `calculator` | ✅ AST 安全计算 |
| `db_query` | ✅ 会话统计 |
| `rag_search` | ✅ TF-IDF 语义检索 |
| `rag_index` / `rag_status` | ✅ 索引与状态 |

**API**：`GET /tools` — 列出已注册工具

**扩展方式**：实现 `Tool` 子类 → `tool_registry.register(MyTool())`

---

### 5️⃣ 前端升级（优先级：P1）

- [ ] 流式 Markdown 优化（减少重渲染抖动）
- [ ] Tool 状态展示 UI（「正在调用 read_file...」卡片）
- [ ] Thinking 状态 UI（工具轮次间的思考动画）
- [ ] 多会话持久化 UI（已从后端加载，需优化删除/重命名）
- [ ] **模型切换下拉框**

---

## 目标架构

```
Vue Frontend
    ↓  /api/chat/stream (SSE)
FastAPI Gateway (server.py)
    ↓
Agent Core (agent.py)
    ↓
Model Router (DeepSeek / Qwen / GPT / Claude)
    ↓
Tool System (File / RAG / DB / Web / Calculator)
    ↓
Storage (SQLite/MySQL + Vector DB/FAISS)
```

---

## 开发约定

1. **SSE 事件类型**不可随意改名，改动需同步 `llm.py` → `agent.py` → `server.py` → `api/chat.js`
2. **新增工具**走 ToolRegistry，不要直接改 `TOOL_HANDLERS` dict
3. **新增模型**实现 `BaseModelProvider`，注册到 `ModelRouter`
4. **会话 ID** 统一用字符串（`String(Date.now())`）
5. **不要**使用 `app/main.py`（废弃 mock）

---

## 环境变量（.env）

```env
API_KEY=sk-...
BASE_URL=https://api.deepseek.com/v1
MODEL=deepseek-v4-flash
DEFAULT_MODEL=deepseek-v4-flash

# 多模型（按需配置）
# QWEN_API_KEY=
# QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# OPENAI_API_KEY=
# OPENAI_BASE_URL=https://api.openai.com/v1
```

---

## 推荐实施顺序

1. **Model Router** — 解耦 llm.py，前端加模型选择
2. **SQLite 数据库** — 替换 JSON 持久化
3. **Tool Registry** — 重构 tools.py
4. **RAG** — FAISS + embedding + rag_search 工具
5. **前端 polish** — tool/thinking UI、模型切换

---

*最后更新：2026-07-03*
