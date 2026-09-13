"""Structured logging configuration for Theater Critics System."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """Setup structured logging for the theater critics system.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        log_format: Custom log format string
        
    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(funcName)s:%(lineno)d - %(message)s"
        )
    
    # Create logger
    logger = logging.getLogger("theater_critics")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "theater_critics") -> logging.Logger:
    """Get configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Performance tracking decorator
def log_performance(func):
    """Decorator to log function performance metrics."""
    import time
    from functools import wraps
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = time.time()
        
        try:
            logger.debug(f"Starting {func.__name__} with args: {len(args)}, kwargs: {len(kwargs)}")
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {execution_time:.2f}s: {str(e)}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = time.time()
        
        try:
            logger.debug(f"Starting {func.__name__} with args: {len(args)}, kwargs: {len(kwargs)}")
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {execution_time:.2f}s: {str(e)}")
            raise
    
    # Return appropriate wrapper based on function type
    if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
        return async_wrapper
    else:
        return sync_wrapper
