"""
System 2.1: Metrics Emitter & Observability Dashboard
Implementation of L.3: System Metrics & Real-time Health Monitoring
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, timedelta
import json
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum
import time

@dataclass
class SystemMetrics:
    """Core system metrics data structure"""
    timestamp: str
    nav: float
    used_margin_pct: float
    free_margin: float
    gssi_score: float
    current_mrc_regime: str
    active_sentinel_mode: str
    llm_feature_hunt_pnl_delta: float
    current_ece_value: float
    open_positions_count: int
    daily_pnl: float
    system_state: str
    
class MetricsEmitter:
    """
    L.3: Dedicated Metrics Emitter for real-time health data
    Exposes live values for monitoring and alerting
    """
    
    def __init__(self):
        self.metrics_history = []
        self.current_metrics = None
        self.alert_thresholds = {
            "max_used_margin_pct": 80.0,
            "max_gssi_score": 0.8,
            "max_ece_value": 0.05,
            "min_free_margin": 1000.0,
            "max_daily_drawdown_pct": 5.0
        }
        self.last_update = None
        
    def update_metrics(self, account_data: Dict[str, Any], 
                      system_components: Dict[str, Any]) -> SystemMetrics:
        """
        Update all system metrics from various components
        """
        from src.core.trace_logger import system_logger
        
        # Extract core account metrics
        nav = account_data.get("nav", 0.0)
        used_margin = account_data.get("used_margin", 0.0)
        free_margin = account_data.get("free_margin", 0.0)
        
        used_margin_pct = (used_margin / nav * 100) if nav > 0 else 0.0
        
        # Extract system component metrics
        gssi_score = system_components.get("gssi_score", 0.0)
        mrc_regime = system_components.get("mrc_regime", "unknown")
        sentinel_mode = system_components.get("sentinel_mode", "stand_down")
        llm_pnl_delta = system_components.get("llm_ab_test_pnl_delta", 0.0)
        ece_value = system_components.get("ece_value", 0.0)
        
        # Trading metrics
        open_positions = system_components.get("open_positions_count", 0)
        daily_pnl = system_components.get("daily_pnl", 0.0)
        system_state = system_components.get("system_state", "normal")
        
        # Create metrics object
        metrics = SystemMetrics(
            timestamp=datetime.utcnow().isoformat(),
            nav=round(nav, 2),
            used_margin_pct=round(used_margin_pct, 2),
            free_margin=round(free_margin, 2),
            gssi_score=round(gssi_score, 4),
            current_mrc_regime=mrc_regime,
            active_sentinel_mode=sentinel_mode,
            llm_feature_hunt_pnl_delta=round(llm_pnl_delta, 2),
            current_ece_value=round(ece_value, 4),
            open_positions_count=open_positions,
            daily_pnl=round(daily_pnl, 2),
            system_state=system_state
        )
        
        self.current_metrics = metrics
        self.last_update = datetime.utcnow()
        
        # Add to history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1440:  # Keep 24 hours of minute data
            self.metrics_history.pop(0)
        
        # Check for alerts
        alerts = self._check_alert_conditions(metrics)
        
        # Log metrics
        metrics_dict = asdict(metrics)
        metrics_dict["alerts"] = alerts
        system_logger.logger.info("SYSTEM_METRICS_UPDATED", **metrics_dict)
        
        return metrics
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics"""
        return self.current_metrics
    
    def get_metrics_json(self) -> str:
        """Get current metrics as JSON string"""
        if self.current_metrics:
            return json.dumps(asdict(self.current_metrics), indent=2)
        return json.dumps({"status": "no_metrics_available"})
    
    def get_metrics_history(self, hours: int = 1) -> List[SystemMetrics]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            metrics for metrics in self.metrics_history
            if datetime.fromisoformat(metrics.timestamp) >= cutoff_time
        ]
    
    def _check_alert_conditions(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """Check metrics against alert thresholds"""
        alerts = []
        
        # Used margin alert
        if metrics.used_margin_pct > self.alert_thresholds["max_used_margin_pct"]:
            alerts.append({
                "type": "HIGH_MARGIN_USAGE",
                "severity": "WARNING",
                "value": metrics.used_margin_pct,
                "threshold": self.alert_thresholds["max_used_margin_pct"],
                "message": f"Margin usage at {metrics.used_margin_pct}%"
            })
        
        # GSSI alert
        if metrics.gssi_score > self.alert_thresholds["max_gssi_score"]:
            alerts.append({
                "type": "HIGH_SYSTEMIC_STRESS",
                "severity": "WARNING", 
                "value": metrics.gssi_score,
                "threshold": self.alert_thresholds["max_gssi_score"],
                "message": f"GSSI score elevated at {metrics.gssi_score}"
            })
        
        # ECE alert
        if metrics.current_ece_value > self.alert_thresholds["max_ece_value"]:
            alerts.append({
                "type": "CALIBRATION_DEGRADATION",
                "severity": "CRITICAL",
                "value": metrics.current_ece_value,
                "threshold": self.alert_thresholds["max_ece_value"],
                "message": f"ECE breach detected at {metrics.current_ece_value}"
            })
        
        # Free margin alert
        if metrics.free_margin < self.alert_thresholds["min_free_margin"]:
            alerts.append({
                "type": "LOW_FREE_MARGIN",
                "severity": "WARNING",
                "value": metrics.free_margin,
                "threshold": self.alert_thresholds["min_free_margin"],
                "message": f"Free margin low at ${metrics.free_margin}"
            })
        
        # Daily drawdown alert
        daily_drawdown_pct = abs(min(0, metrics.daily_pnl)) / metrics.nav * 100
        if daily_drawdown_pct > self.alert_thresholds["max_daily_drawdown_pct"]:
            alerts.append({
                "type": "EXCESSIVE_DRAWDOWN",
                "severity": "CRITICAL",
                "value": daily_drawdown_pct,
                "threshold": self.alert_thresholds["max_daily_drawdown_pct"],
                "message": f"Daily drawdown at {daily_drawdown_pct}%"
            })
        
        return alerts
    
    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format for external monitoring
        """
        if not self.current_metrics:
            return "# No metrics available\n"
        
        metrics = self.current_metrics
        timestamp_ms = int(time.time() * 1000)
        
        prometheus_metrics = f"""# HELP forex_nav Net Asset Value
# TYPE forex_nav gauge
forex_nav {metrics.nav} {timestamp_ms}

# HELP forex_used_margin_pct Used Margin Percentage  
# TYPE forex_used_margin_pct gauge
forex_used_margin_pct {metrics.used_margin_pct} {timestamp_ms}

# HELP forex_free_margin Free Margin
# TYPE forex_free_margin gauge
forex_free_margin {metrics.free_margin} {timestamp_ms}

# HELP forex_gssi_score Global Systemic Stress Indicator
# TYPE forex_gssi_score gauge
forex_gssi_score {metrics.gssi_score} {timestamp_ms}

# HELP forex_ece_value Expected Calibration Error
# TYPE forex_ece_value gauge  
forex_ece_value {metrics.current_ece_value} {timestamp_ms}

# HELP forex_open_positions Open Positions Count
# TYPE forex_open_positions gauge
forex_open_positions {metrics.open_positions_count} {timestamp_ms}

# HELP forex_daily_pnl Daily P&L
# TYPE forex_daily_pnl gauge
forex_daily_pnl {metrics.daily_pnl} {timestamp_ms}

# HELP forex_llm_ab_test_pnl LLM A/B Test P&L Delta
# TYPE forex_llm_ab_test_pnl gauge
forex_llm_ab_test_pnl {metrics.llm_feature_hunt_pnl_delta} {timestamp_ms}
"""
        
        return prometheus_metrics

class SystemHealthDashboard:
    """
    Real-time system health dashboard aggregator
    Combines metrics from all system components
    """
    
    def __init__(self, metrics_emitter: MetricsEmitter):
        self.metrics_emitter = metrics_emitter
        self.component_status = {}
        self.last_health_check = None
    
    async def get_system_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive system health report
        """
        current_time = datetime.utcnow()
        
        # Get current metrics
        current_metrics = self.metrics_emitter.get_current_metrics()
        
        if not current_metrics:
            return {
                "status": "ERROR",
                "message": "No metrics available",
                "timestamp": current_time.isoformat()
            }
        
        # Calculate overall health score
        health_score = self._calculate_health_score(current_metrics)
        
        # Get component statuses
        component_statuses = await self._check_component_health()
        
        # Get recent performance
        performance_summary = self._get_performance_summary()
        
        # Determine overall status
        overall_status = self._determine_overall_status(health_score, component_statuses)
        
        health_report = {
            "timestamp": current_time.isoformat(),
            "overall_status": overall_status,
            "health_score": health_score,
            "current_metrics": asdict(current_metrics),
            "component_statuses": component_statuses,
            "performance_summary": performance_summary,
            "alerts": self.metrics_emitter._check_alert_conditions(current_metrics),
            "system_uptime": self._get_system_uptime(),
            "last_update": self.metrics_emitter.last_update.isoformat() if self.metrics_emitter.last_update else None
        }
        
        self.last_health_check = current_time
        return health_report
    
    def _calculate_health_score(self, metrics: SystemMetrics) -> float:
        """
        Calculate overall system health score (0-100)
        """
        score = 100.0
        
        # Margin health (20% weight)
        if metrics.used_margin_pct > 80:
            score -= 20 * (metrics.used_margin_pct - 80) / 20
        
        # Stress health (25% weight)  
        if metrics.gssi_score > 0.5:
            score -= 25 * (metrics.gssi_score - 0.5) / 0.5
        
        # Calibration health (25% weight)
        if metrics.current_ece_value > 0.03:
            score -= 25 * (metrics.current_ece_value - 0.03) / 0.07
        
        # P&L health (15% weight)
        daily_return_pct = (metrics.daily_pnl / metrics.nav * 100) if metrics.nav > 0 else 0
        if daily_return_pct < -3:  # More than 3% daily loss
            score -= 15 * abs(daily_return_pct + 3) / 2
        
        # System state health (15% weight)
        if metrics.system_state != "normal":
            if metrics.system_state in ["weight_lock", "recalibration"]:
                score -= 10  # Moderate penalty
            elif metrics.system_state in ["route_diversion", "halt"]:
                score -= 15  # High penalty
        
        return max(0.0, min(100.0, round(score, 1)))
    
    async def _check_component_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of individual system components"""
        
        # This would integrate with actual component health checks
        # For now, return mock statuses
        
        component_statuses = {
            "market_data_feed": {
                "status": "HEALTHY",
                "last_update": datetime.utcnow().isoformat(),
                "latency_ms": 50
            },
            "broker_connection": {
                "status": "HEALTHY", 
                "last_ping": datetime.utcnow().isoformat(),
                "connection_stable": True
            },
            "llm_engine": {
                "status": "HEALTHY",
                "model_loaded": True,
                "avg_response_time_ms": 1200
            },
            "risk_engine": {
                "status": "HEALTHY",
                "last_check": datetime.utcnow().isoformat(),
                "constraints_active": True
            },
            "calibration_engine": {
                "status": "HEALTHY",
                "ece_within_limits": True,
                "recalibration_due": False
            }
        }
        
        return component_statuses
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get recent performance summary"""
        
        # Get recent metrics
        recent_metrics = self.metrics_emitter.get_metrics_history(hours=24)
        
        if len(recent_metrics) < 2:
            return {"status": "insufficient_data"}
        
        # Calculate performance metrics
        latest = recent_metrics[-1]
        earliest = recent_metrics[0]
        
        nav_change = latest.nav - earliest.nav
        nav_change_pct = (nav_change / earliest.nav * 100) if earliest.nav > 0 else 0.0
        
        # Average metrics over period
        avg_gssi = sum([m.gssi_score for m in recent_metrics]) / len(recent_metrics)
        avg_margin_usage = sum([m.used_margin_pct for m in recent_metrics]) / len(recent_metrics)
        
        # Trade statistics
        total_positions = sum([m.open_positions_count for m in recent_metrics])
        
        return {
            "period_hours": 24,
            "nav_change": round(nav_change, 2),
            "nav_change_pct": round(nav_change_pct, 2),
            "avg_gssi_score": round(avg_gssi, 4),
            "avg_margin_usage_pct": round(avg_margin_usage, 2),
            "total_position_time": total_positions,
            "data_points": len(recent_metrics)
        }
    
    def _determine_overall_status(self, health_score: float, 
                                component_statuses: Dict[str, Dict[str, Any]]) -> str:
        """Determine overall system status"""
        
        # Check for critical component failures
        critical_components = ["broker_connection", "risk_engine"]
        for component in critical_components:
            if (component in component_statuses and 
                component_statuses[component].get("status") != "HEALTHY"):
                return "CRITICAL"
        
        # Determine status based on health score
        if health_score >= 90:
            return "HEALTHY"
        elif health_score >= 70:
            return "WARNING"
        elif health_score >= 50:
            return "DEGRADED"
        else:
            return "CRITICAL"
    
    def _get_system_uptime(self) -> Dict[str, Any]:
        """Get system uptime information"""
        # This would track actual system start time
        # For now, return mock uptime
        
        uptime_seconds = 86400  # 24 hours mock
        uptime_hours = uptime_seconds / 3600
        
        return {
            "uptime_seconds": uptime_seconds,
            "uptime_hours": round(uptime_hours, 1),
            "uptime_days": round(uptime_hours / 24, 1)
        }

# Global instances
metrics_emitter = MetricsEmitter()
health_dashboard = SystemHealthDashboard(metrics_emitter)