"""
Logging configuration for the Movi Transport Agent.

Provides structured logging with different levels for different components.
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Add timestamp
        record.timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Format the message first
        formatted = super().format(record)

        # Add color to level name in the formatted message
        if hasattr(record, 'levelname') and record.levelname in self.COLORS:
            color_prefix = self.COLORS[record.levelname]
            color_suffix = self.RESET
            # Replace level name with colored version
            formatted = formatted.replace(record.levelname, f"{color_prefix}{record.levelname}{color_suffix}")

        return formatted


def setup_logger(
    name: str,
    level: str = "INFO",
    format_string: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string
        use_colors: Whether to use colored output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    # Set formatter
    if format_string is None:
        format_string = "[%(timestamp)s] %(levelname)-8s | %(name)s: %(message)s"

    if use_colors:
        formatter = ColoredFormatter(format_string)
    else:
        formatter = logging.Formatter(format_string)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with consistent configuration.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    # Configure logging if not already done
    if not logging.getLogger().handlers:
        setup_logger("movi_agent", level="INFO")

    return logging.getLogger(name)


# Agent-specific loggers
agent_logger = setup_logger("movi_agent.agent", level="INFO")
tool_logger = setup_logger("movi_agent.tools", level="INFO")
api_logger = setup_logger("movi_agent.api", level="INFO")
db_logger = setup_logger("movi_agent.database", level="WARNING")  # Less verbose for DB