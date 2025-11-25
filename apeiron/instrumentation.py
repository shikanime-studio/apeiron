import logging
import os

# TODO: Mlflow doesn't support Langchain 1.0
# import mlflow
import uvicorn
from langchain_core.globals import set_debug

logger = logging.getLogger(__name__)


def get_logging_level() -> int:
    """Get the logging level from the environment variable.
    Returns:
        Logging level as an integer
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    level_names = logging.getLevelNamesMapping()
    try:
        return level_names[log_level_str.upper()]
    except KeyError as e:
        raise ValueError(f"Invalid log level: {log_level_str}") from e


def create_logging_handlers():
    match os.getenv("LOG_FORMAT", "uvicorn"):
        case "uvicorn":
            handler = logging.StreamHandler()
            handler.setFormatter(
                uvicorn.logging.DefaultFormatter("%(levelprefix)s %(message)s")
            )
            return [handler]
        case _:
            return []


def init():
    # TODO: Mlflow doesn't support Langchain 1.0
    # Intrumentalise the langchain_core with mlflow
    # mlflow.langchain.autolog()
    if os.getenv("DEBUG", "false").lower() == "true":
        set_debug(True)

    # Get log level from environment variable, default to INFO if not set
    logging.basicConfig(level=get_logging_level(), handlers=create_logging_handlers())
