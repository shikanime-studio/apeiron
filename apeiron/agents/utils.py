from os import PathLike

import yaml
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def _validate_message(message: dict) -> bool:
    """Validate if message has required fields."""
    return isinstance(message, dict) and "role" in message and "content" in message


def _create_message(
    role: str, content: str
) -> HumanMessage | AIMessage | SystemMessage | None:
    """Create appropriate message type based on role."""
    if not content:
        return None

    if role == "system":
        return SystemMessage(content=content)
    elif role == "human":
        return HumanMessage(content=content)
    elif role == "ai":
        return AIMessage(content=content)
    else:
        raise ValueError(f"Invalid role: {role}")


def load_prompt(path: PathLike) -> SystemMessage:
    """Load a system prompt as a SystemMessage from the YAML file."""
    with open(path) as f:
        prompt_config = yaml.safe_load(f)
    if not prompt_config:
        raise ValueError("Empty prompt configuration file")
    message = prompt_config.get("system_message", "")
    if not message:
        raise ValueError("Empty message content")
    return SystemMessage(content=message)
