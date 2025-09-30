import structlog
import logging
import sys
from .config import settings

def setup_logging():
    """Configure structured logging for the application"""
    
    # Production logging configuration
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # In production, use WARNING level to reduce noise
    if settings.ENVIRONMENT == "production":
        log_level = logging.WARNING
    
    # Configure Python logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = "default"):
    """Get a structured logger instance"""
    return structlog.get_logger(name)
