import logging
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver

from apeiron.agents.utils import load_prompt

logger = logging.getLogger(__name__)


def create_operation_60_agent(**kwargs) -> BaseChatModel:
    """Create the Operator 6O agent for the graph.

    Args:
        tools: Sequence of tools available to the agent
        model: Base chat model to use
        **kwargs: Additional arguments passed to create_react_agent

    Returns:
        Configured chat model agent
    """
    return create_agent(
        name="Operator 6O",
        checkpointer=InMemorySaver(),
        system_prompt=load_prompt(
            Path(__file__).parent.resolve() / f"{Path(__file__).stem}.yaml",
        ),
        **kwargs,
    )
