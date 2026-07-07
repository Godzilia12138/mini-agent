"""会话持久化 — SQLite 后端。"""

from app.db.repository import repo





def list_sessions() -> list:

    return repo.list_sessions()





def get_session(session_id: str) -> dict | None:

    return repo.get_session(session_id)





def save_session(

    session_id: str,

    title: str,

    messages: list,

    files: dict,

    model: str = "deepseek-v4-flash",

):

    repo.save_session(session_id, title, messages, files, model)





def delete_session(session_id: str):

    repo.delete_session(session_id)





def session_exists(session_id: str) -> bool:

    return repo.session_exists(session_id)





def save_message(session_id: str, role: str, content: str):

    repo.save_message(session_id, role, content)





def load_messages(session_id: str) -> list:

    return repo.load_messages(session_id)





def save_file(session_id: str, filename: str, content: str):

    repo.save_file(session_id, filename, content)





def create_session_record(

    session_id: str,

    title: str = "新对话",

    model: str | None = None,

):

    repo.create_session(session_id, title, model)





def update_session_meta(session_id: str, title: str | None = None, model: str | None = None):

    repo.update_session_meta(session_id, title, model)


