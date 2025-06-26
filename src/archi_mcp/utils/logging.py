"""Logging configuration for ArchiMate MCP server."""

import sys
from typing import Optional

from loguru import logger


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    file_path: Optional[str] = None,
) -> None:
    """Setup logging configuration for the ArchiMate MCP server.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        file_path: Optional file path for log output
    """
    # Remove default handler
    logger.remove()
    
    # Default format
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=format_string,
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler if specified
    if file_path:
        logger.add(
            file_path,
            format=format_string,
            level=level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )
    
    logger.info(f"Logging configured with level: {level}")


def get_logger(name: str) -> "logger":
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)