from langchain.memory import ConversationBufferWindowMemory
from typing import Dict


_memory_store: Dict[str, ConversationBufferWindowMemory] = {}


def get_conversation_memory(session_id: str = "default", k: int = 10) -> ConversationBufferWindowMemory:
    if session_id not in _memory_store:
        _memory_store[session_id] = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=k,
            return_messages=True
        )
    return _memory_store[session_id]


def clear_conversation_memory(session_id: str = "default"):
    if session_id in _memory_store:
        _memory_store[session_id].clear()


def clear_all_memories():
    _memory_store.clear()
