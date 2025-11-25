import logging
from pathlib import Path

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from apeiron.agents.utils import load_prompt

logger = logging.getLogger(__name__)


def create_roast_agent(**kwargs):
    """Create the roast generation node for the graph."""
    return create_agent(
        name="Roast",
        checkpointer=InMemorySaver(),
        system_prompt=load_prompt(
            Path(__file__).parent.resolve() / f"{Path(__file__).stem}.yaml",
        ),
        **kwargs,
    )
