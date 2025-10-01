import logging

logger = logging.getLogger(__name__)


def create_agent(agent: str, **kwargs):
    """Create an agent instance by name with the provided kwargs.

    Args:
        name: The name of the agent to create ('operator_6o', 'teto', 'roast')
        **kwargs: Arguments to pass to the agent's create_agent function

    Returns:
        The created agent instance

    Raises:
        ValueError: If the agent name is unknown or import fails
    """
    try:
        if agent == "operator_6o":
            from apeiron.agents.operator_6o import create_agent as _create_agent
        elif agent == "teto":
            from apeiron.agents.teto import create_agent as _create_agent
        elif agent == "roast":
            from apeiron.agents.roast import create_agent as _create_agent
        else:
            raise ValueError(f"Unknown agent: {agent}")

        return _create_agent(**kwargs)
    except ImportError as e:
        logger.error(f"Failed to import agent '{agent}': {e}")
        raise ValueError(f"Agent '{agent}' is not available") from e
