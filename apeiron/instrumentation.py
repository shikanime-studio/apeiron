import logging
import os

import mlflow
import uvicorn

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
    # Intrumentalise the langchain_core with mlflow
    mlflow.langchain.autolog()

    # Get log level from environment variable, default to INFO if not set
    logging.basicConfig(level=get_logging_level(), handlers=create_logging_handlers())
