<div align="center">
  <br>
  <img src="https://img.shields.io/badge/Python-3.10+-2b5b84?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue_3-4FC08D?logo=vuedotjs" alt="Vue 3">
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <br><br>

  <h1>🤖 Mini Agent</h1>
  <p><strong>轻量级 AI Agent 平台</strong> — 多模型路由 · 工具调用 · RAG 知识库 · MCP 扩展</p>

  <p>
    <a href="#-架构">架构</a> ·
    <a href="#-功能特性">功能</a> ·
    <a href="#-快速开始">快速开始</a> ·
    <a href="#-项目结构">结构</a> ·
    <a href="#-技术亮点">技术亮点</a>
  </p>

  <br>
</div>

---

## 🏗️ 架构

```
┌──────────────────────────────────────────────────────────────┐
│                      Vue 3 前端                               │
│         SSE (text/event-stream) ↔ REST API                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   FastAPI 网关 (server.py)                    │
│         路由 · 文件上传 · 会话 CRUD · SSE 流式                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   Agent 核心 (agent.py)                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   Tool Loop（工具循环）                  │  │
│  │                                                         │  │
│  │  用户输入 → 构造消息 → 调用 LLM → 解析响应               │  │
│  │                                      │                  │  │
│  │                              ┌───────▼────────┐        │  │
│  │                              │ 有 tool_call?  │        │  │
│  │                              └───┬───┬─────────┘        │  │
│  │                                 No  Yes                 │  │
│  │                               ┌─▼┐ ┌──▼──────────┐     │  │
│  │                               │★│ │  执行工具     │     │  │
│  │                               │†│ │ → 继续循环    │     │  │
│  │                               └─┘ └──────────────┘     │  │
│  └────────────────────────────────────────────────────────┘  │
│  · 滑动窗口上下文管理（12K 字符限制）                           │
│  · 原生思考链（deepseek/qwen/kimi/glm 推理 API）              │
│  · 最大 6~8 步 tool loop                                      │
└──────────────────┬───────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬─────────────────┐
    │              │              │                  │
┌───▼────┐  ┌─────▼─────┐  ┌────▼─────┐  ┌───────▼────────┐
│ 模型   │  │ Provider  │  │ 工具系统  │  │ MCP 桥接      │
│ 路由   │  │ 层        │  │          │  │ (外部)         │
│        │  │           │  │          │  │                │
│ Deep-  │  │ OpenAI    │  │ 文件读写  │  │ ClientSession  │
│ Seek   │  │ 兼容协议   │  │ 计算器   │  │ Group          │
│ Qwen   │  │ SSE/JSON  │  │ RAG 检索 │  │                │
│ Kimi   │  │ 自动重试   │  │ 数据库   │  │ 后台事件循环   │
│ GLM    │  │ 原生思考   │  │ Web     │  │ → 工具注入     │
│ OpenAI │  │           │  │ (可扩展) │  │                │
└────────┘  └───────────┘  └──────────┘  └─────────────────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
    ┌────▼──┐ ┌───▼────┐ ┌──▼─────┐
    │ RAG   │ │ 记忆   │ │ SQLite │
    │       │ │        │ │        │
    │ 分块   │ │ chat[] │ │ 会话   │
    │ 嵌入   │ │ files  │ │ 消息   │
    │ 索引   │ │        │ │ 文件   │
    │ 检索   │ │        │ │        │
    └───────┘ └────────┘ └────────┘
```

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🧠 **多模型路由** | DeepSeek / Qwen / Kimi / GLM / OpenAI，会话级别动态切换 |
| 🔧 **工具调用** | 文件读写、计算器、数据库查询、RAG 语义检索，通过 Tool 基类可扩展 |
| 🧩 **MCP 支持** | 接入外部 MCP 服务器，运行时动态注入远程工具 |
| 📄 **文件分析** | 上传 .txt / .md / .py / .docx / .pdf 等文件，自动索引到 RAG 知识库 |
| 💬 **SSE 流式输出** | 逐 token 实时推送，事件类型包括 thinking / token / status / done |
| 🧠 **原生思考** | 通过 API 参数开启模型原生推理能力（非 prompt 模拟） |
| 📚 **RAG 知识库** | 文档分块 → TF-IDF 嵌入 → 语义检索，完整流水线 |
| 🗂️ **多会话管理** | 创建/切换/删除会话，SQLite 持久化 |
| 📊 **结构化日志** | 自动脱敏敏感信息，记录 Token 用量、API 延迟、工具执行耗时 |

---

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
# 编辑 .env，至少配置 DEEPSEEK_API_KEY

# 5. 启动服务
uvicorn app.server:app --reload --port 8000
```

### 前端

```bash
cd mini-agent/frontend
npm install
npm run dev
```

打开 **http://localhost:5173** 🎉

---

## ⚙️ 配置 (.env)

```env
# ── 必填 ──
DEEPSEEK_API_KEY=sk-xxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# ── 可选：扩展模型 ──
QWEN_API_KEY=sk-xxxxxxxx
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
KIMI_API_KEY=sk-xxxxxxxx
GLM_API_KEY=sk-xxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxx

# ── 默认模型 ──
MODEL=deepseek-chat
```

---

## 📁 项目结构

```
mini-agent/
├── app/                          # 后端
│   ├── server.py                 # FastAPI 入口：路由、SSE 流式、文件上传
│   ├── agent.py                  # Agent 核心：Tool Loop、上下文管理
│   ├── router.py                 # ModelRouter：注册表模式多模型路由
│   ├── config.py                 # 环境配置加载
│   ├── logger.py                 # 统一日志（控制台 + 文件滚动）
│   ├── thinking.py               # 原生思考 API 参数注入
│   ├── session.py                # 会话管理器
│   ├── memory.py                 # 每会话聊天记忆
│   ├── persistence.py            # SQLite 持久化（自动从 JSON 迁移）
│   ├── models.py                 # SQLAlchemy 模型（session / message / file）
│   ├── providers/                # LLM 提供商适配
│   │   ├── base.py               # 抽象 BaseModelProvider
│   │   └── openai_compat.py      # OpenAI 兼容：SSE、重试、思考模式
│   ├── tools/                    # 可扩展工具系统
│   │   ├── base.py               # Tool 抽象基类
│   │   ├── registry.py           # ToolRegistry（注册 / 执行 / 获取定义）
│   │   ├── file_tools.py         # 文件读写/搜索工具
│   │   ├── calculator.py         # AST 安全计算器
│   │   ├── rag_tools.py          # RAG 搜索/索引/状态工具
│   │   └── extended_tools.py     # 数据库查询、网页搜索（预留）
│   ├── rag/                      # RAG 知识库
│   │   ├── chunker.py            # 文本分块（重叠、段落感知）
│   │   ├── embedder.py           # TF-IDF / API / 本地嵌入
│   │   ├── store.py              # 向量存储
│   │   ├── indexer.py            # 索引流水线
│   │   ├── retriever.py          # 搜索结果格式化
│   │   └── service.py            # rag_service 单例
│   ├── mcp/                      # MCP 客户端桥接
│   │   ├── bridge.py             # 后台 asyncio 线程 + ClientSessionGroup
│   │   ├── config.py             # MCP 服务器配置加载
│   │   └── tool_adapter.py       # 将 MCP 工具包装为 Tool 接口
│   └── db/                       # SQLite 数据库
│       ├── database.py           # 连接与 schema
│       └── repository.py         # SessionRepository
├── frontend/                     # Vue 3 前端
│   └── src/
│       ├── App.vue               # 主应用编排
│       ├── api/                  # SSE fetch 封装
│       ├── components/           # UI 组件
│       └── utils/                # Markdown 渲染
├── .env.example                  # 环境变量模板
├── requirements.txt
└── AGENTS.md                     # 开发文档
```

---

## 🧩 支持的模型

| 提供商 | 模型 | 状态 |
|--------|------|------|
| DeepSeek | `deepseek-chat`, `deepseek-v4-flash` | ✅ |
| 阿里云 Qwen | `qwen-plus`, `qwen-turbo`, `qwen-max` | ✅ |
| Moonshot Kimi | `moonshot-v1-32k`, `kimi-k2` | ✅ |
| 智谱 GLM | `glm-4-flash`, `glm-4`, `glm-4-plus` | ✅ |
| OpenAI | `gpt-4o-mini` | ✅ |
| *自定义* | 任意 OpenAI 兼容 API | ✅ 5 行代码接入 |

---

## 🏆 技术亮点

### 使用的设计模式

| 模式 | 位置 | 作用 |
|------|------|------|
| **注册表模式** | ModelRouter / ToolRegistry | 新增模型或工具只需注册，核心代码零改动 |
| **策略模式** | Provider 层 | 统一接口，不同模型不同行为（思考模式、重试策略） |
| **生产者-消费者** | MCP 桥接（同步→异步） | 线程安全地执行工具，不阻塞事件循环 |
| **单例模式** | `rag_service`, `mcp_bridge` | 共享状态，避免全局变量 |
| **模板方法** | `Tool.execute()` | 统一错误处理，每个工具只实现自身逻辑 |

### 关键工程决策

| 决策 | 理由 |
|------|------|
| **不用 LangChain** | 完全掌控 Tool Loop，不框架锁定，方便调试 |
| **用 SSE 而不是 WebSocket** | 协议简单，HTTP 原生，兼容标准负载均衡器 |
| **统一 OpenAI 兼容协议** | 一个 Provider 适配器覆盖 5+ 模型家族 |
| **默认用 TF-IDF 做 RAG** | 零外部依赖，离线可用，单次检索 0.1ms |
| **滑动窗口上下文** | 防止 token 溢出，同时保留最近对话 |
| **日志自动脱敏** | API Key 和用户数据不会写入日志文件 |

### 为什么这是 Agent 而不是 Chat Bot

| 能力 | 实现方式 |
|------|---------|
| **工具选择** | LLM 通过 function calling 自主选择工具，不是硬编码 |
| **多步推理** | Tool Loop 最多 8 步，每次结果回注上下文 |
| **自主处理文件** | 上传 → 保存 → RAG 索引 → 语义可检索 |
| **外部工具** | MCP 服务器运行时动态注入工具 |
| **思考/推理** | API 级别的原生思考（非 prompt 模拟） |

---

## 📊 API 概览

### SSE 流式接口（主要）

```
POST /chat/stream
Content-Type: multipart/form-data

message=你好&session_id=abc&thinking=true
```

响应事件：

| 类型 | 说明 |
|------|------|
| `thinking` | 模型推理内容 |
| `token` | 文本内容 delta |
| `status` | 工具调用状态 |
| `done` | 完成，包含完整回答 |
| `error` | 错误信息 |

### REST 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 健康检查 |
| `GET` | `/models` | 列出可用模型 |
| `GET` | `/tools` | 列出已注册工具 |
| `GET` | `/sessions` | 会话列表 |
| `POST` | `/sessions` | 新建会话 |
| `GET` | `/sessions/{id}` | 会话历史 |
| `PUT` | `/sessions/{id}/model` | 切换模型 |
| `DELETE` | `/sessions/{id}` | 删除会话 |
| `GET` | `/rag/status` | 知识库状态 |
| `GET` | `/rag/search?q=...` | 语义检索调试 |
| `GET` | `/mcp/status` | MCP 连接状态 |

---

## 🔧 扩展指南

### 新增模型

```python
# 1. app/router.py — 注册一行
self._add("my-model", "provider", "my-model-id", "我的模型")

# 2. app/config.py — 添加凭证
# MY_MODEL_API_KEY=sk-xxx
# 完成。OpenAI 兼容 Provider 自动处理剩下的事。
```

### 新增工具

```python
from app.tools.base import Tool

class MyTool(Tool):
    name = "my_tool"
    description = "做一些有用的事"
    parameters = {
        "type": "object",
        "properties": {"input": {"type": "string"}},
        "required": ["input"],
    }

    def execute(self, args: dict) -> str:
        return f"你好, {args['input']}!"

# 在 app/tools/__init__.py 中注册
tool_registry.register(MyTool())
```

---

## 📄 开源协议

[MIT](LICENSE)

---

<div align="center">
  <sub>Built with FastAPI · Vue 3 · SQLite · 🤖</sub>
</div>
