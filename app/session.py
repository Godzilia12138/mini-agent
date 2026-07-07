from app.agent import Agent
from app import persistence
from app.router import model_router


class SessionManager:

    def __init__(self):
        self.sessions: dict[str, Agent] = {}

    def get_agent(self, session_id: str) -> Agent:
        if session_id not in self.sessions:
            stored = persistence.get_session(session_id)
            agent = Agent(session_id=session_id)
            if stored:
                agent.load_from_store(stored)
            self.sessions[session_id] = agent
        return self.sessions[session_id]

    def save(self, session_id: str):
        agent = self.sessions.get(session_id)
        if not agent:
            return
        data = agent.to_store()
        persistence.save_session(
            session_id,
            data["title"],
            data["messages"],
            data["files"],
            data.get("model", model_router.default_model_id),
        )

    def save_message(self, session_id: str, role: str, content: str):
        """增量保存单条消息到数据库。"""
        persistence.save_message(session_id, role, content)
        agent = self.sessions.get(session_id)
        if agent:
            persistence.update_session_meta(session_id, title=agent.title, model=agent.model)

    def list_sessions(self) -> list:
        return persistence.list_sessions()

    def get_history(self, session_id: str) -> dict | None:
        stored = persistence.get_session(session_id)
        if not stored:
            return None
        return {
            "id": session_id,
            "title": stored.get("title", "新对话"),
            "model": stored.get("model", model_router.default_model_id),
            "messages": stored.get("messages", []),
        }

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
        persistence.delete_session(session_id)

    def create_session(self, session_id: str, title: str = "新对话", model: str | None = None) -> Agent:
        mid = model_router.resolve_model_id(model)
        agent = Agent(session_id=session_id, title=title, model=mid)
        self.sessions[session_id] = agent
        persistence.create_session_record(session_id, title, mid)
        return agent

    def update_model(self, session_id: str, model_id: str):
        agent = self.get_agent(session_id)
        agent.set_model(model_id)
        persistence.update_session_meta(session_id, model=agent.model)
        return agent.model

    def save_file(self, session_id: str, filename: str, content: str):
        persistence.save_file(session_id, filename, content)
        agent = self.sessions.get(session_id)
        if agent:
            agent.memory.add_file(filename, content)
