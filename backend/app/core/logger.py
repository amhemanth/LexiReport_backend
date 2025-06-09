"""Logger configuration."""
import logging
import sys
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger instance
logger = logging.getLogger("app")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(f"app.{name}")

def log_error(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None) -> None:
    """Log an error with context."""
    if context:
        logger.error(f"{str(error)} - Context: {context}")
    else:
        logger.error(str(error))

def log_info(logger: logging.Logger, message: str, context: Dict[str, Any] = None) -> None:
    """Log an info message with context."""
    if context:
        logger.info(f"{message} - Context: {context}")
    else:
        logger.info(message)

def log_warning(logger: logging.Logger, message: str, context: Dict[str, Any] = None) -> None:
    """Log a warning message with context."""
    if context:
        logger.warning(f"{message} - Context: {context}")
    else:
        logger.warning(message)

def log_debug(logger: logging.Logger, message: str, context: Dict[str, Any] = None) -> None:
    """Log a debug message with context."""
    if context:
        logger.debug(f"{message} - Context: {context}")
    else:
        logger.debug(message) 