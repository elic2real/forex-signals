import structlog
import logging
import sys
from .config import settings

def setup_logging():
    """Configure structured logging and metrics for the application"""
    import prometheus_client
    # Production logging configuration
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    if settings.ENVIRONMENT == "production":
        log_level = logging.WARNING
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
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
    # Prometheus metrics
    global METRICS
    METRICS = {
        "win_rate": prometheus_client.Gauge("win_rate", "Win percentage"),
        "expectancy": prometheus_client.Gauge("expectancy", "Expectancy per trade"),
        "trade_latency": prometheus_client.Gauge("trade_latency", "Trade latency in ms"),
        "gate_block_ratio": prometheus_client.Gauge("gate_block_ratio", "Ratio of blocked trades by gates"),
        "readiness_score": prometheus_client.Gauge("readiness_score", "Hourly readiness score")
    }

def audit_log(event: str, details: dict):
    import uuid
    trace_id = str(uuid.uuid4())
    print({"audit": event, "trace_id": trace_id, **details})

def log_metric(name: str, value: float):
    if 'METRICS' in globals() and name in METRICS:
        METRICS[name].set(value)

def get_logger(name: str = "default"):
    """Get a structured logger instance"""
    return structlog.get_logger(name)
