class MemoryManager:

    def __init__(self):
        self.memory_store = {}

    def load(self, user_id: str):
        return self.memory_store.get(user_id, {})

    def save(self, user_id: str, data: dict):
        self.memory_store[user_id] = data
