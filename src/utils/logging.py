"""
Logging configuration for Racing Analysis system.
Uses loguru for structured logging with rotation and formatting.
"""

import sys
from loguru import logger
from pathlib import Path
from src.utils.config import settings


def setup_logging():
    """Configure application logging"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler (pretty output for development)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )
    
    # File handler (structured logs for production)
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,  # Thread-safe
    )
    
    logger.info(f"Logging initialized (level={settings.log_level}, file={settings.log_file})")
    
    return logger


# Initialize logging on import
log = setup_logging()
