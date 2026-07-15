import io
import json
import os
import time

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from docx import Document

from app.logger import get_logger, _sanitize
from app.session import SessionManager
from app.tools import WORKSPACE
from app.router import model_router
from app.thinking import parse_thinking, supports_native_thinking

log = get_logger(__name__)

app = FastAPI(title="Mini AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = SessionManager()

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


def read_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def save_upload(filename: str, content: bytes) -> str:
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            413,
            f"文件过大：{len(content) / 1024 / 1024:.1f} MB，最大允许 {MAX_UPLOAD_SIZE / 1024 / 1024:.0f} MB"
        )
    safe_name = os.path.basename(filename)
    dest = os.path.join(WORKSPACE, safe_name)
    with open(dest, "wb") as f:
        f.write(content)
    if safe_name.endswith(".docx"):
        return read_docx(content)
    return content.decode("utf-8", errors="ignore")


def _index_to_rag(filename: str, text: str):
    """上传文件后自动索引到 RAG 知识库。"""
    if not text or not text.strip():
        return
    try:
        from app.rag.service import rag_service
        rag_service.index_document(filename, text)
    except Exception:
        pass  # RAG 索引失败不阻断聊天


def _sse_event(data: dict) -> bytes:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


@app.get("/thinking")
def thinking_info():
    from app.router import model_router
    models = []
    for m in model_router.list_models():
        pid = m["id"]
        try:
            p = model_router.get_provider(pid)
            native = getattr(p, "supports_thinking", lambda: False)()
        except Exception:
            native = False
        models.append({"id": pid, "name": m["name"], "supports_thinking": native})
    return {
        "param": "thinking",
        "values": ["true", "false"],
        "default": False,
        "description": "原生思考：通过 API 参数开启，返回 reasoning_content",
        "models": models,
    }


@app.get("/modes")
def list_thinking_modes_legacy():
    """兼容旧接口，映射到 thinking。"""
    return {
        "modes": [
            {"id": "normal", "label": "普通模式", "thinking": False},
            {"id": "think", "label": "思考模式（已废弃，请用 thinking=true）", "thinking": True},
        ],
        "default": "normal",
        "use": "POST /chat/stream 传 thinking=true/false",
    }


@app.get("/health")
def health():
    from app.config import ENV_FILE, env, default_model
    default = model_router.get_provider()
    return {
        "status": "ok",
        "model": default_model(),
        "default": model_router.default_model_id,
        "default_model_name": default.display_name,
        "api_configured": default.is_available(),
        "env_file": str(ENV_FILE),
        "env_exists": ENV_FILE.is_file(),
        "base_url": env("BASE_URL", ""),
    }


@app.get("/models")
def list_models():
    from app.config import default_model, provider_credentials
    providers_status = {}
    for name in ("deepseek", "qwen", "kimi", "glm"):
        key, url = provider_credentials(name)
        providers_status[name] = {"configured": bool(key), "base_url": url}
    return {
        "models": model_router.list_models(),
        "default": model_router.default_model_id,
        "env_model": default_model(),
        "providers": providers_status,
    }


@app.get("/tools")
def list_tools():
    from app.tools import tool_registry
    tools = tool_registry.list_tools()
    mcp_info = None
    try:
        from app.mcp.tool_adapter import mcp_tools_registered
        from app.mcp.bridge import get_mcp_bridge
        from app.mcp.config import mcp_enabled
        if mcp_enabled():
            mcp_info = get_mcp_bridge().status()
    except Exception:
        pass
    return {"tools": tools, "mcp": mcp_info, "mcp_active": mcp_tools_registered() if mcp_info else False}


@app.get("/mcp/status")
def mcp_status():
    from app.mcp.config import mcp_enabled, load_mcp_servers
    from app.mcp.bridge import get_mcp_bridge
    if not mcp_enabled():
        return {"enabled": False, "message": "MCP 未启用，设置 MCP_ENABLED=true 或配置 mcp_servers.json"}
    bridge = get_mcp_bridge()
    if not bridge.tools and load_mcp_servers():
        bridge.start(load_mcp_servers())
    return {"enabled": True, **bridge.status()}


@app.post("/mcp/reload")
def mcp_reload():
    from app.mcp.bridge import reload_mcp_bridge
    from app.mcp.tool_adapter import register_mcp_tools
    from app.tools import tool_registry
    status = reload_mcp_bridge()
    added = register_mcp_tools(tool_registry)
    return {"ok": True, "registered": added, **status}


@app.get("/rag/status")
def rag_status():
    from app.rag.service import rag_service
    return rag_service.stats()


@app.get("/rag/search")
def rag_search_api(q: str, top_k: int = 5):
    from app.rag.service import rag_service
    from app.rag.indexer import search
    from app.rag.retriever import format_search_results
    results = search(q, top_k=top_k)
    return {"query": q, "results": results, "formatted": format_search_results(results)}


@app.post("/rag/index")
async def rag_index_file(path: str = Form(...)):
    from app.rag.service import rag_service
    try:
        count = rag_service.index_workspace_file(path)
        return {"ok": True, "path": path, "chunks": count}
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/files")
def list_workspace_files():
    from app.tools import list_files
    return {"files": list_files()}


# ── 会话 CRUD ──

@app.get("/sessions")
def get_sessions():
    return {"sessions": sessions.list_sessions()}


@app.post("/sessions")
def create_session(
    session_id: str = Form(...),
    title: str = Form("新对话"),
    model: str = Form(None),
):
    if sessions.get_history(session_id):
        raise HTTPException(409, "会话已存在")
    agent = sessions.create_session(session_id, title, model)
    return {"id": session_id, "title": agent.title, "model": agent.model}


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    history = sessions.get_history(session_id)
    if not history:
        raise HTTPException(404, "会话不存在")
    return history


@app.put("/sessions/{session_id}/model")
def update_session_model(session_id: str, model: str = Form(...)):
    try:
        mid = sessions.update_model(session_id, model)
        return {"id": session_id, "model": mid}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    sessions.delete_session(session_id)
    return {"ok": True}


# ── 流式聊天（SSE） ──

@app.post("/chat/stream")
async def chat_stream_endpoint(
    message: str = Form(""),
    file: UploadFile = File(None),
    session_id: str = Form("default"),
    model: str = Form(None),
    thinking: str = Form("false"),
    mode: str = Form(None),
):
    req_time = time.time()
    agent = sessions.get_agent(session_id)
    thinking_enabled = parse_thinking(thinking if mode is None else mode)

    log.info(
        "请求 | session=%s | model=%s | thinking=%s | upload=%s | msg=%s",
        session_id[:8] if session_id else "default",
        model or agent.model,
        thinking_enabled,
        file.filename if file else "无",
        _sanitize(message, 80),
    )

    if model:
        try:
            agent.set_model(model)
        except ValueError as e:
            async def err():
                yield _sse_event({"type": "error", "content": str(e)})
            return StreamingResponse(err(), media_type="text/event-stream; charset=utf-8")

    if file and file.filename:
        content = await file.read()
        text = save_upload(file.filename, content)
        sessions.save_file(session_id, file.filename, text)
        _index_to_rag(file.filename, text)

    if not message.strip() and not file:
        async def empty():
            yield _sse_event({"type": "error", "content": "请输入消息或上传文件。"})
        return StreamingResponse(empty(), media_type="text/event-stream; charset=utf-8")

    task = message or "请分析我上传的文件内容。"

    def generate():
        try:
            for event in agent.run_stream(task, thinking=thinking_enabled):
                yield _sse_event(event)
                if event["type"] == "done":
                    sessions.save(session_id)
        except ValueError as e:
            log.error("请求配置错误 | session=%s | err=%s", session_id[:8], e)
            yield _sse_event({"type": "error", "content": f"⚠️ 配置错误：{e}"})
        except RuntimeError as e:
            log.error("请求 API 失败 | session=%s | err=%s", session_id[:8], e)
            yield _sse_event({"type": "error", "content": f"⚠️ API 调用失败：{e}"})
        except Exception as e:
            log.error("请求异常 | session=%s | err=%s", session_id[:8], e, exc_info=True)
            yield _sse_event({"type": "error", "content": f"⚠️ 发生错误：{e}"})
        else:
            total = time.time() - req_time
            log.info("请求完成 | session=%s | 总耗时=%.2fs", session_id[:8], total)
        finally:
            agent_model = getattr(agent, "model", "?")
            total = time.time() - req_time
            log.info(
                "请求结束 | session=%s | model=%s | 总耗时=%.2fs",
                session_id[:8], agent_model, total,
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── 兼容旧接口 ──

@app.post("/chat")
async def chat(
    message: str = Form(""),
    file: UploadFile = File(None),
    session_id: str = Form("default"),
    model: str = Form(None),
    thinking: str = Form("false"),
    mode: str = Form(None),
):
    agent = sessions.get_agent(session_id)
    thinking_enabled = parse_thinking(thinking if mode is None else mode)
    if model:
        agent.set_model(model)

    if file and file.filename:
        content = await file.read()
        text = save_upload(file.filename, content)
        sessions.save_file(session_id, file.filename, text)
        _index_to_rag(file.filename, text)

    if not message.strip() and not file:
        return {"answer": "请输入消息或上传文件。"}

    full = ""
    try:
        for event in agent.run_stream(message or "请分析我上传的文件内容。", thinking=thinking_enabled):
            if event["type"] == "token":
                full += event["content"]
            elif event["type"] == "done":
                full = event["content"]
                sessions.save(session_id)
                break
            elif event["type"] == "error":
                full = event["content"]
                break
    except Exception as e:
        full = f"⚠️ 发生错误：{e}"

    return {"answer": full, "model": agent.model}
