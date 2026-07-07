class Memory:
    def __init__(self):
        self.chat = []
        self.files = {}

    def add_chat(self, role, content):
        self.chat.append({"role": role, "content": content})

    def add_file(self, filename, content):
        self.files[filename] = content

    def get_chat_history(self):
        return "\n".join(
            f"{m['role']}: {m['content']}" for m in self.chat
        )

    def get_files(self):
        return self.files