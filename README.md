<div align="center">
  <br>
  <img src="https://img.shields.io/badge/Python-3.10+-2b5b84?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue_3-4FC08D?logo=vuedotjs" alt="Vue 3">
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <br><br>

  <h1>🤖 Mini Agent</h1>
  <p><strong>A lightweight, extensible AI Agent platform with multi-model routing, tool calling, RAG knowledge base, and MCP support.</strong></p>

  <p>
    <a href="#-architecture">Architecture</a> ·
    <a href="#-features">Features</a> ·
    <a href="#-quick-start">Quick Start</a> ·
    <a href="#-project-structure">Structure</a> ·
    <a href="#-technical-highlights">Highlights</a>
  </p>

  <br>
</div>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Vue 3 Frontend                             │
│         SSE (text/event-stream) ↔ REST API                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                  FastAPI Gateway (server.py)                   │
│    Routing · File Upload · Session CRUD · SSE Streaming       │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                  Agent Core (agent.py)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    Tool Loop                            │  │
│  │                                                         │  │
│  │  User Input → Build Messages → Call LLM → Parse Response│  │
│  │                                        │                │  │
│  │                                ┌───────▼────────┐      │  │
│  │                                │ Has tool_call?  │      │  │
│  │                                └───┬───┬─────────┘      │  │
│  │                                   No  Yes               │  │
│  │                                 ┌─▼┐ ┌──▼──────────┐    │  │
│  │                                 │★│ │ Execute Tool │    │  │
│  │                                 │†│ │ → Continue   │    │  │
│  │                                 └─┘ └──────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│  · Sliding-window context management (12K char limit)        │
│  · Native thinking (deepseek/qwen/kimi/glm reasoning API)    │
│  · Max 6-8 tool-loop steps                                   │
└──────────────────┬───────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬─────────────────┐
    │              │              │                  │
┌───▼────┐  ┌─────▼─────┐  ┌────▼─────┐  ┌───────▼────────┐
│ Model  │  │ Provider  │  │ Tools    │  │ MCP Bridge     │
│ Router │  │ Layer     │  │ System   │  │ (external)     │
│        │  │           │  │          │  │                │
│ Deep-  │  │ OpenAI    │  │ File R/W  │  │ ClientSession  │
│ Seek   │  │ Compat    │  │ Calc     │  │ Group          │
│ Qwen   │  │ Protocol  │  │ RAG      │  │                │
│ Kimi   │  │ SSE/JSON  │  │ DB Query │  │ Background     │
│ GLM    │  │ Retry     │  │ Web      │  │ event loop     │
│ OpenAI │  │ Thinking  │  │ (extend) │  │ → Tool injection│
└────────┘  └───────────┘  └──────────┘  └─────────────────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
    ┌────▼──┐ ┌───▼────┐ ┌──▼─────┐
    │ RAG   │ │Memory  │ │ SQLite │
    │       │ │        │ │        │
    │chunk  │ │chat[]  │ │sessions│
    │embed  │ │files   │ │messages│
    │index  │ │        │ │files   │
    │retrieve│ │        │ │        │
    └───────┘ └────────┘ └────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Multi-Model Routing** | DeepSeek / Qwen / Kimi / GLM / OpenAI — switch at runtime per session |
| 🔧 **Tool Calling** | File read/write, calculator, DB query, RAG search — extensible via `Tool` base class |
| 🧩 **MCP Support** | Connect external MCP servers to inject remote tools dynamically |
| 📄 **File Analysis** | Upload `.txt`, `.md`, `.py`, `.js`, `.docx`, `.pdf` etc., auto-index into RAG |
| 💬 **SSE Streaming** | Real-time token-by-token streaming with `thinking` / `token` / `status` / `done` events |
| 🧠 **Native Thinking** | Enables model-native reasoning (deepseek `thinking` param, qwen `enable_thinking`, etc.) |
| 📚 **RAG Knowledge Base** | Document chunking → TF-IDF embedding → semantic retrieval pipeline |
| 🗂️ **Multi-Session** | Create / switch / delete sessions with SQLite persistence |
| 📊 **Structured Logging** | Auto-sanitized logging with token usage, API latency, tool execution tracing |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend

```bash
# 1. Clone
git clone https://github.com/Godzilia12138/mini-agent.git
cd mini-agent

# 2. Virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env — at least DEEPSEEK_API_KEY is required

# 5. Start the server
uvicorn app.server:app --reload --port 8000
```

### Frontend

```bash
cd mini-agent/frontend
npm install
npm run dev
```

Open **http://localhost:5173** 🎉

---

## ⚙️ Configuration (.env)

```env
# ── Required ──
DEEPSEEK_API_KEY=sk-xxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# ── Optional: Additional Models ──
QWEN_API_KEY=sk-xxxxxxxx
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
KIMI_API_KEY=sk-xxxxxxxx
GLM_API_KEY=sk-xxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxx

# ── Model Selection ──
MODEL=deepseek-chat
```

---

## 📁 Project Structure

```
mini-agent/
├── app/                          # Backend
│   ├── server.py                 # FastAPI entry: routes, SSE streaming, file upload
│   ├── agent.py                  # Agent core: tool loop, context management
│   ├── router.py                 # ModelRouter: registry-pattern multi-model routing
│   ├── config.py                 # Environment configuration
│   ├── logger.py                 # Unified logging (console + RotatingFileHandler)
│   ├── thinking.py               # Native thinking API parameter injection
│   ├── session.py                # Session manager
│   ├── memory.py                 # Per-session chat memory
│   ├── persistence.py            # SQLite persistence (auto-migrates from JSON)
│   ├── models.py                 # SQLAlchemy models (session, message, file)
│   ├── providers/                # LLM provider adapters
│   │   ├── base.py               # Abstract BaseModelProvider
│   │   └── openai_compat.py      # OpenAI-compatible: SSE, retry, thinking
│   ├── tools/                    # Extensible tool system
│   │   ├── base.py               # Tool abstract base class
│   │   ├── registry.py           # ToolRegistry (register / execute / get_definitions)
│   │   ├── file_tools.py         # File read/write/search tools
│   │   ├── calculator.py         # AST-safe math evaluator
│   │   ├── rag_tools.py          # RAG search/index/status tools
│   │   └── extended_tools.py     # DB query, web search (placeholder)
│   ├── rag/                      # RAG knowledge base
│   │   ├── chunker.py            # Text chunking (overlap, paragraph-aware)
│   │   ├── embedder.py           # TF-IDF / API / local embedding
│   │   ├── store.py              # Vector storage
│   │   ├── indexer.py            # Indexing pipeline
│   │   ├── retriever.py          # Search result formatting
│   │   └── service.py            # rag_service singleton
│   ├── mcp/                      # MCP client bridge
│   │   ├── bridge.py             # Background asyncio thread + ClientSessionGroup
│   │   ├── config.py             # MCP server config loader
│   │   └── tool_adapter.py       # Wraps MCP tools into Tool interface
│   └── db/                       # SQLite database
│       ├── database.py           # Connection & schema
│       └── repository.py         # SessionRepository
├── frontend/                     # Vue 3 frontend
│   └── src/
│       ├── App.vue               # Main orchestrator
│       ├── api/                  # SSE fetch wrapper
│       ├── components/           # UI components
│       └── utils/                # Markdown renderer
├── .env.example                  # Environment template
├── requirements.txt
└── AGENTS.md                     # Development guide
```

---

## 🧩 Supported Models

| Provider | Models | Status |
|----------|--------|--------|
| DeepSeek | `deepseek-chat`, `deepseek-v4-flash` | ✅ |
| Alibaba Qwen | `qwen-plus`, `qwen-turbo`, `qwen-max` | ✅ |
| Moonshot Kimi | `moonshot-v1-32k`, `kimi-k2` | ✅ |
| Zhipu GLM | `glm-4-flash`, `glm-4`, `glm-4-plus` | ✅ |
| OpenAI | `gpt-4o-mini` | ✅ |
| *Custom* | Any OpenAI-compatible API | ✅ Add 5 lines |

---

## 🏆 Technical Highlights

### Design Patterns

| Pattern | Where | Why |
|---------|-------|-----|
| **Registry** | `ModelRouter` / `ToolRegistry` | New model or tool = register, zero core changes |
| **Strategy** | Provider layer | Same interface, different model behavior (thinking, retry) |
| **Producer-Consumer** | MCP bridge (sync→async) | Thread-safe tool execution without blocking event loop |
| **Singleton** | `rag_service`, `mcp_bridge` | Shared state without global variables |
| **Template Method** | `Tool.execute()` | Uniform error handling, each tool only implements its logic |

### Engineering Decisions

| Decision | Rationale |
|----------|-----------|
| **No LangChain** | Full control over tool loop, no framework lock-in, easier to debug |
| **SSE over WebSocket** | Simpler protocol, HTTP-native, works with standard load balancers |
| **OpenAI-compatible protocol** | One provider adapter covers 5+ model families |
| **TF-IDF as default RAG** | Zero external dependencies, works offline, 0.1ms retrieval |
| **Sliding window context** | Prevents token overflow without losing recent conversation |
| **Auto-sanitized logging** | API keys and user data never written to log files |

### What Makes This an Agent (Not a Chat Bot)

| Capability | Implementation |
|------------|---------------|
| Tool selection | LLM chooses tools via `function calling`, not hardcoded |
| Multi-step reasoning | Tool loop up to 8 steps, results fed back into context |
| Autonomous file handling | Upload → save → RAG index → semantically retrievable |
| External tooling | MCP servers inject tools dynamically at runtime |
| Thinking/Reasoning | Native API-level thinking (not prompt-simulated) |

---

## 📊 API Overview

### SSE Streaming (Primary)

```
POST /chat/stream
Content-Type: multipart/form-data

message=你好&session_id=abc&thinking=true
```

Response events:

| Type | Description |
|------|-------------|
| `thinking` | Model reasoning content |
| `token` | Text content delta |
| `status` | Tool invocation status |
| `done` | Completion with full answer |
| `error` | Error message |

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/models` | List available models |
| `GET` | `/tools` | List registered tools |
| `GET` | `/sessions` | List sessions |
| `POST` | `/sessions` | Create session |
| `GET` | `/sessions/{id}` | Get session history |
| `PUT` | `/sessions/{id}/model` | Switch model |
| `DELETE` | `/sessions/{id}` | Delete session |
| `GET` | `/rag/status` | RAG knowledge base stats |
| `GET` | `/rag/search?q=...` | Semantic search debug |
| `GET` | `/mcp/status` | MCP connection status |

---

## 🔧 Extending

### Add a New Model

```python
# 1. app/router.py — register once
self._add("my-model", "provider", "my-model-id", "My Model")

# 2. app/config.py — add credentials
# MY_MODEL_API_KEY=sk-xxx
# Done. The OpenAI-compatible provider handles the rest.
```

### Add a New Tool

```python
from app.tools.base import Tool

class MyTool(Tool):
    name = "my_tool"
    description = "Does something useful"
    parameters = {
        "type": "object",
        "properties": {"input": {"type": "string"}},
        "required": ["input"],
    }

    def execute(self, args: dict) -> str:
        return f"Hello, {args['input']}!"

# Register in app/tools/__init__.py
tool_registry.register(MyTool())
```

---

## 📄 License

[MIT](LICENSE)

---

<div align="center">
  <sub>Built with FastAPI · Vue 3 · SQLite · and a lot of tool calls 🤖</sub>
</div>
