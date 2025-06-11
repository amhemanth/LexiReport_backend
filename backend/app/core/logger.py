"""Logger configuration."""
import logging
import sys
import os
from typing import Any, Dict
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Disable all existing handlers and console output
for logger_name in logging.root.manager.loggerDict:
    logging.getLogger(logger_name).handlers = []
    logging.getLogger(logger_name).propagate = False

# Disable root logger console output
logging.getLogger().handlers = []
logging.getLogger().propagate = False

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.propagate = False

# Create formatters
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create handlers for different log types
app_handler = logging.FileHandler(LOGS_DIR / "app.log")
app_handler.setFormatter(file_formatter)
app_handler.setLevel(logging.INFO)

database_handler = logging.FileHandler(LOGS_DIR / "database.log")
database_handler.setFormatter(file_formatter)
database_handler.setLevel(logging.INFO)

error_handler = logging.FileHandler(LOGS_DIR / "error.log")
error_handler.setFormatter(file_formatter)
error_handler.setLevel(logging.WARNING)

api_handler = logging.FileHandler(LOGS_DIR / "api.log")
api_handler.setFormatter(file_formatter)
api_handler.setLevel(logging.INFO)

# Create console handler for API logs
api_console_handler = logging.StreamHandler(sys.stdout)
api_console_handler.setFormatter(console_formatter)
api_console_handler.setLevel(logging.INFO)

# Add handlers to root logger
root_logger.addHandler(app_handler)
root_logger.addHandler(database_handler)
root_logger.addHandler(error_handler)
root_logger.addHandler(api_handler)

# Create logger instance
logger = logging.getLogger("app")
logger.propagate = False

def setup_file_handler(logger_name: str, log_file: str, level: int = logging.INFO, console: bool = False) -> logging.Logger:
    """Set up a file handler for a specific logger."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False
    
    # Create file handler
    handler = logging.FileHandler(LOGS_DIR / log_file)
    handler.setFormatter(file_formatter)
    handler.setLevel(level)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Add file handler to logger
    logger.addHandler(handler)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    
    return logger

# Set up specific loggers
database_logger = setup_file_handler("app.database", "database.log")
audit_logger = setup_file_handler("app.audit", "audit.log")
error_logger = setup_file_handler("app.error", "error.log")
task_logger = setup_file_handler("app.tasks", "tasks.log")
api_logger = setup_file_handler("app.api", "api.log", console=True)  # Enable console output for API logs
security_logger = setup_file_handler("app.security", "security.log")

# Configure SQLAlchemy logger
sqlalchemy_logger = setup_file_handler("sqlalchemy.engine", "database.log")
sqlalchemy_logger.setLevel(logging.INFO)

# Configure Uvicorn logger
uvicorn_logger = setup_file_handler("uvicorn", "app.log")
uvicorn_logger.setLevel(logging.INFO)

# Configure Uvicorn access logger
uvicorn_access_logger = setup_file_handler("uvicorn.access", "api.log", console=True)  # Enable console output for access logs
uvicorn_access_logger.setLevel(logging.INFO)

# Configure Pydantic logger
pydantic_logger = setup_file_handler("pydantic", "error.log")
pydantic_logger.setLevel(logging.WARNING)

# For backward compatibility, alias db_logger to database_logger
db_logger = database_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    logger = logging.getLogger(f"app.{name}")
    logger.propagate = False
    return logger

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