"""Logging configuration."""

import logging
import logging.handlers
import os
from pathlib import Path


def setup_logger(
    name: str = "netstalker",
    log_level: int = logging.INFO,
    log_dir: str = "logs"
) -> logging.Logger:
    """Configure application logger.
    
    Args:
        name: Logger name
        log_level: Logging level
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    # Create logs directory
    Path(log_dir).mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, f"{name}.log"),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
