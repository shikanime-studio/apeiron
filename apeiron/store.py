from langchain.embeddings import init_embeddings
from langgraph.store.memory import InMemoryStore


def create_store(model: str, **kwargs) -> InMemoryStore:
    """Create a memory store."""
    return InMemoryStore(
        index={
            "dims": 1536,
            "embed": init_embeddings(model, **kwargs),
            "fields": ["text"],
        }
    )
