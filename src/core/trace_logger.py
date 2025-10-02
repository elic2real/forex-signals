"""
System 2.1: Structured Logging & Traceability Infrastructure
Implementation of L.1, L.2, L.3 requirements for production observability
"""

import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum
import structlog
from contextlib import contextmanager
import threading

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class GuardrailStatus(Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"

class TraceContext:
    """Thread-local trace context for carrying trace IDs through pipeline"""
    _local = threading.local()
    
    @classmethod
    def get_trace_id(cls) -> str:
        return getattr(cls._local, 'trace_id', str(uuid.uuid4()))
    
    @classmethod
    def set_trace_id(cls, trace_id: str):
        cls._local.trace_id = trace_id
    
    @classmethod
    def new_trace(cls) -> str:
        trace_id = str(uuid.uuid4())
        cls.set_trace_id(trace_id)
        return trace_id

class SystemLogger:
    """
    Production-grade structured logger for System 2.1
    Implements all L.1, L.2, L.3 requirements
    """
    
    def __init__(self):
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
        self.logger = structlog.get_logger()
    
    def _base_event(self, instrument: str, extra_fields: Optional[Dict] = None) -> Dict[str, Any]:
        """Base event structure with mandatory fields"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": TraceContext.get_trace_id(),
            "instrument": instrument,
            "system": "forex_signals_v2.1"
        }
        if extra_fields:
            event.update(extra_fields)
        return event
    
    # L.1: Structured Logging Implementation
    def log_context_tick(self, instrument: str, ctx: Dict[str, Any]):
        """Log full context object at M1 tick - DEBUG level"""
        event = self._base_event(instrument, {
            "event_type": "context_tick",
            "context": ctx,
            "level": LogLevel.DEBUG.value
        })
        self.logger.debug("M1_CONTEXT_TICK", **event)
    
    def log_guardrail_check(self, instrument: str, gate_name: str, 
                          status: GuardrailStatus, reason: str, 
                          value: Optional[float] = None, threshold: Optional[float] = None):
        """Log guardrail gate checks with status and reason"""
        level = LogLevel.WARN if status == GuardrailStatus.BLOCK else LogLevel.INFO
        event = self._base_event(instrument, {
            "event_type": "guardrail_check",
            "gate_name": gate_name,
            "status": status.value,
            "reason": reason,
            "value": value,
            "threshold": threshold,
            "level": level.value
        })
        
        if status == GuardrailStatus.BLOCK:
            self.logger.warning("GUARDRAIL_BLOCK", **event)
        else:
            self.logger.info("GUARDRAIL_PASS", **event)
    
    # L.2: Critical Event Debugging
    def log_supervisor_decision(self, instrument: str, input_scores: Dict[str, float], 
                              output_decision: Dict[str, Any]):
        """Log complete supervisor decision audit trail"""
        event = self._base_event(instrument, {
            "event_type": "supervisor_decision",
            "input_scores": input_scores,
            "output_decision": output_decision,
            "level": LogLevel.INFO.value
        })
        self.logger.info("SUPERVISOR_DECISION", **event)
    
    def log_broker_api_failure(self, instrument: str, api_request: Dict[str, Any], 
                             api_response: Dict[str, Any], gssi_score: float, error: str):
        """Log CRITICAL broker API failures with full context"""
        event = self._base_event(instrument, {
            "event_type": "broker_api_failure",
            "api_request": api_request,
            "api_response": api_response,
            "gssi_score": gssi_score,
            "error": error,
            "level": LogLevel.CRITICAL.value
        })
        self.logger.critical("BROKER_API_FAILURE", **event)
    
    def log_mandatory_weight_lock(self, instrument: str, ece_value: float, 
                                ece_threshold: float, lock_timestamp: str, 
                                recalibration_start: str):
        """Log CRITICAL calibration degradation events (P.1)"""
        event = self._base_event(instrument, {
            "event_type": "mandatory_weight_lock",
            "ece_value": ece_value,
            "ece_threshold": ece_threshold,
            "ece_breach": ece_value > ece_threshold,
            "lock_timestamp": lock_timestamp,
            "recalibration_start": recalibration_start,
            "level": LogLevel.CRITICAL.value
        })
        self.logger.critical("MANDATORY_WEIGHT_LOCK", **event)
    
    def log_liquidity_cliff_emergency(self, instrument: str, spread_ratio: float, 
                                    cancelled_orders: int, market_exits: int):
        """Log emergency liquidity cliff actions"""
        event = self._base_event(instrument, {
            "event_type": "liquidity_cliff_emergency",
            "spread_ratio": spread_ratio,
            "cancelled_orders": cancelled_orders,
            "market_exits": market_exits,
            "level": LogLevel.CRITICAL.value
        })
        self.logger.critical("LIQUIDITY_CLIFF_EMERGENCY", **event)
    
    def log_drawdown_kill_switch(self, instrument: str, daily_drawdown_pct: float, 
                               peak_nav: float, current_nav: float, trades_flattened: int):
        """Log kill switch activation"""
        event = self._base_event(instrument, {
            "event_type": "drawdown_kill_switch",
            "daily_drawdown_pct": daily_drawdown_pct,
            "peak_nav": peak_nav,
            "current_nav": current_nav,
            "trades_flattened": trades_flattened,
            "level": LogLevel.CRITICAL.value
        })
        self.logger.critical("DRAWDOWN_KILL_SWITCH", **event)

# Global logger instance
system_logger = SystemLogger()

@contextmanager
def trace_pipeline(instrument: str, operation: str):
    """Context manager for tracing complete pipeline operations"""
    trace_id = TraceContext.new_trace()
    start_time = time.time()
    
    system_logger.logger.info("PIPELINE_START", 
                            trace_id=trace_id,
                            instrument=instrument,
                            operation=operation,
                            timestamp=datetime.utcnow().isoformat())
    try:
        yield trace_id
    except Exception as e:
        system_logger.logger.error("PIPELINE_ERROR",
                                 trace_id=trace_id,
                                 instrument=instrument,
                                 operation=operation,
                                 error=str(e),
                                 timestamp=datetime.utcnow().isoformat())
        raise
    finally:
        duration = time.time() - start_time
        system_logger.logger.info("PIPELINE_END",
                                trace_id=trace_id,
                                instrument=instrument,
                                operation=operation,
                                duration_seconds=duration,
                                timestamp=datetime.utcnow().isoformat())