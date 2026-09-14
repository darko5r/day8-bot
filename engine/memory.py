from engine.models import ConversationMemory


class MemoryStore:
    """In-memory scoped storage.

    A scope can later be a Discord tuple such as:
    (guild_id, channel_id, user_id)

    For the terminal runner we use one fixed scope.
    """

    def __init__(self):
        self._memories: dict[tuple[str, str, str], ConversationMemory] = {}

    def get(self, scope: tuple[str, str, str]) -> ConversationMemory:
        if scope not in self._memories:
            self._memories[scope] = ConversationMemory()
        return self._memories[scope]

    def reset(self, scope: tuple[str, str, str]) -> ConversationMemory:
        self._memories[scope] = ConversationMemory()
        return self._memories[scope]
