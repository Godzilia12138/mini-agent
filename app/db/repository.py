import json
import os
from datetime import datetime

from app.db.database import get_connection, init_db, DATA_DIR, _lock
from app.router import model_router

JSON_STORE = os.path.join(DATA_DIR, "sessions.json")


def _now() -> str:
    return datetime.now().isoformat()


class SessionRepository:

    def __init__(self):
        init_db()

    def list_sessions(self) -> list:
        with _lock:
            conn = get_connection()
            try:
                rows = conn.execute("""
                    SELECT s.id, s.title, s.model, s.updated_at,
                           COUNT(m.id) AS message_count
                    FROM sessions s
                    LEFT JOIN messages m ON m.session_id = s.id
                    GROUP BY s.id
                    ORDER BY s.updated_at DESC
                """).fetchall()
                return [
                    {
                        "id": r["id"],
                        "title": r["title"],
                        "model": r["model"],
                        "updated_at": r["updated_at"],
                        "message_count": r["message_count"],
                    }
                    for r in rows
                ]
            finally:
                conn.close()

    def get_session(self, session_id: str) -> dict | None:
        with _lock:
            conn = get_connection()
            try:
                row = conn.execute(
                    "SELECT * FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()
                if not row:
                    return None
                messages = self._load_messages_conn(conn, session_id)
                files = self._load_files_conn(conn, session_id)
                return {
                    "title": row["title"],
                    "model": row["model"],
                    "messages": messages,
                    "files": files,
                    "updated_at": row["updated_at"],
                }
            finally:
                conn.close()

    def session_exists(self, session_id: str) -> bool:
        with _lock:
            conn = get_connection()
            try:
                row = conn.execute(
                    "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()
                return row is not None
            finally:
                conn.close()

    def create_session(
        self,
        session_id: str,
        title: str = "新对话",
        model: str | None = None,
    ):
        mid = model_router.resolve_model_id(model)
        now = _now()
        with _lock:
            conn = get_connection()
            try:
                conn.execute(
                    """INSERT INTO sessions (id, title, model, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (session_id, title, mid, now, now),
                )
                conn.commit()
            finally:
                conn.close()

    def update_session_meta(
        self,
        session_id: str,
        title: str | None = None,
        model: str | None = None,
    ):
        with _lock:
            conn = get_connection()
            try:
                fields, params = [], []
                if title is not None:
                    fields.append("title = ?")
                    params.append(title)
                if model is not None:
                    fields.append("model = ?")
                    params.append(model_router.resolve_model_id(model))
                if not fields:
                    return
                fields.append("updated_at = ?")
                params.append(_now())
                params.append(session_id)
                conn.execute(
                    f"UPDATE sessions SET {', '.join(fields)} WHERE id = ?",
                    params,
                )
                conn.commit()
            finally:
                conn.close()

    def save_session(
        self,
        session_id: str,
        title: str,
        messages: list,
        files: dict,
        model: str = "deepseek-v4-flash",
    ):
        """全量保存会话（messages + files 替换）。"""
        mid = model_router.resolve_model_id(model)
        now = _now()
        with _lock:
            conn = get_connection()
            try:
                existing = conn.execute(
                    "SELECT id FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()

                if existing:
                    conn.execute(
                        "UPDATE sessions SET title=?, model=?, updated_at=? WHERE id=?",
                        (title, mid, now, session_id),
                    )
                else:
                    conn.execute(
                        """INSERT INTO sessions (id, title, model, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (session_id, title, mid, now, now),
                    )

                conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                for msg in messages:
                    conn.execute(
                        """INSERT INTO messages (session_id, role, content, created_at)
                           VALUES (?, ?, ?, ?)""",
                        (session_id, msg["role"], msg["content"], now),
                    )

                conn.execute("DELETE FROM files WHERE session_id = ?", (session_id,))
                for filename, content in files.items():
                    conn.execute(
                        """INSERT INTO files (session_id, filename, content, created_at)
                           VALUES (?, ?, ?, ?)""",
                        (session_id, filename, content, now),
                    )

                conn.commit()
            finally:
                conn.close()

    def delete_session(self, session_id: str):
        with _lock:
            conn = get_connection()
            try:
                conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                conn.commit()
            finally:
                conn.close()

    def save_message(self, session_id: str, role: str, content: str):
        now = _now()
        with _lock:
            conn = get_connection()
            try:
                conn.execute(
                    """INSERT INTO messages (session_id, role, content, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (session_id, role, content, now),
                )
                conn.execute(
                    "UPDATE sessions SET updated_at = ? WHERE id = ?",
                    (now, session_id),
                )
                conn.commit()
            finally:
                conn.close()

    def load_messages(self, session_id: str) -> list:
        with _lock:
            conn = get_connection()
            try:
                return self._load_messages_conn(conn, session_id)
            finally:
                conn.close()

    def save_file(self, session_id: str, filename: str, content: str):
        now = _now()
        with _lock:
            conn = get_connection()
            try:
                conn.execute(
                    """INSERT INTO files (session_id, filename, content, created_at)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(session_id, filename)
                       DO UPDATE SET content=excluded.content, created_at=excluded.created_at""",
                    (session_id, filename, content, now),
                )
                conn.execute(
                    "UPDATE sessions SET updated_at = ? WHERE id = ?",
                    (now, session_id),
                )
                conn.commit()
            finally:
                conn.close()

    def _load_messages_conn(self, conn, session_id: str) -> list:
        rows = conn.execute(
            """SELECT role, content FROM messages
               WHERE session_id = ? ORDER BY id ASC""",
            (session_id,),
        ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    def _load_files_conn(self, conn, session_id: str) -> dict:
        rows = conn.execute(
            "SELECT filename, content FROM files WHERE session_id = ?",
            (session_id,),
        ).fetchall()
        return {r["filename"]: r["content"] for r in rows}

    def migrate_from_json(self):
        """一次性从 sessions.json 迁移到 SQLite。"""
        if not os.path.exists(JSON_STORE):
            return 0

        with _lock:
            conn = get_connection()
            try:
                count = conn.execute("SELECT COUNT(*) AS c FROM sessions").fetchone()["c"]
                if count > 0:
                    return 0

                with open(JSON_STORE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                migrated = 0
                for sid, s in data.get("sessions", {}).items():
                    self.save_session(
                        sid,
                        s.get("title", "新对话"),
                        s.get("messages", []),
                        s.get("files", {}),
                        s.get("model", model_router.default_model_id),
                    )
                    migrated += 1

                if migrated:
                    backup = JSON_STORE + ".bak"
                    if not os.path.exists(backup):
                        os.rename(JSON_STORE, backup)

                return migrated
            finally:
                conn.close()


repo = SessionRepository()
repo.migrate_from_json()
