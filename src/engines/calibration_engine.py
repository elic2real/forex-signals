"""
System 2.1: Calibration Degradation Audit & Self-Correction Engine
Implementation of P.1 (ECE Audit) and P.2 (Execution Quality Contingency)
"""

from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.calibration import calibration_curve
import pickle
import os

class SystemState(Enum):
    NORMAL = "normal"
    WEIGHT_LOCK = "weight_lock"
    RECALIBRATION = "recalibration"
    ROUTE_DIVERSION = "route_diversion"

class CalibrationDegradationAuditor:
    """
    P.1: Calibration Degradation Audit Engine
    Monitors Expected Calibration Error (ECE) and triggers mandatory weight lock
    """
    
    def __init__(self):
        self.ece_threshold = 0.05  # 5% ECE threshold
        self.weight_lock_duration = timedelta(hours=48)  # 48-hour mandatory lock
        self.recalibration_window = 100  # Minimum samples for recalibration
        
        self.system_state = SystemState.NORMAL
        self.weight_lock_start = None
        self.prediction_history = []  # Store (predicted_prob, actual_outcome) pairs
        self.current_ece = 0.0
        
        # Isotonic regression calibrator
        self.calibrator = IsotonicRegression(out_of_bounds='clip')
        self.calibrator_fitted = False
    
    def add_prediction_outcome(self, predicted_probability: float, actual_outcome: bool, 
                             trade_metadata: Dict[str, Any]):
        """
        Add prediction-outcome pair for ECE monitoring
        """
        from src.core.trace_logger import system_logger
        
        prediction_record = {
            "predicted_prob": predicted_probability,
            "actual_outcome": 1.0 if actual_outcome else 0.0,
            "timestamp": datetime.utcnow(),
            "trade_metadata": trade_metadata
        }
        
        self.prediction_history.append(prediction_record)
        
        # Limit history size for performance
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-1000:]
        
        system_logger.logger.debug("PREDICTION_OUTCOME_RECORDED",
                                 predicted_prob=predicted_probability,
                                 actual_outcome=actual_outcome,
                                 total_predictions=len(self.prediction_history))
    
    def calculate_ece(self, n_bins: int = 10) -> Dict[str, Any]:
        """
        Calculate Expected Calibration Error (ECE)
        ECE = Σ (|accuracy - confidence|) * (bin_weight)
        """
        from src.core.trace_logger import system_logger
        
        if len(self.prediction_history) < 20:  # Minimum samples required
            return {
                "ece": 0.0,
                "insufficient_data": True,
                "sample_count": len(self.prediction_history)
            }
        
        # Extract predictions and outcomes
        predictions = [record["predicted_prob"] for record in self.prediction_history]
        outcomes = [record["actual_outcome"] for record in self.prediction_history]
        
        # Calculate calibration curve
        try:
            fraction_positives, mean_predicted_value = calibration_curve(
                outcomes, predictions, n_bins=n_bins, strategy='uniform'
            )
            
            # Calculate ECE
            bin_boundaries = np.linspace(0, 1, n_bins + 1)
            ece = 0.0
            bin_details = []
            
            for i in range(n_bins):
                # Find predictions in this bin
                bin_mask = (predictions >= bin_boundaries[i]) & (predictions < bin_boundaries[i + 1])
                if i == n_bins - 1:  # Include upper boundary for last bin
                    bin_mask = (predictions >= bin_boundaries[i]) & (predictions <= bin_boundaries[i + 1])
                
                bin_predictions = np.array(predictions)[bin_mask]
                bin_outcomes = np.array(outcomes)[bin_mask]
                
                if len(bin_predictions) > 0:
                    bin_confidence = np.mean(bin_predictions)
                    bin_accuracy = np.mean(bin_outcomes)
                    bin_weight = len(bin_predictions) / len(predictions)
                    
                    bin_ece = abs(bin_accuracy - bin_confidence) * bin_weight
                    ece += bin_ece
                    
                    bin_details.append({
                        "bin_index": i,
                        "bin_range": [float(bin_boundaries[i]), float(bin_boundaries[i + 1])],
                        "confidence": round(bin_confidence, 4),
                        "accuracy": round(bin_accuracy, 4),
                        "count": len(bin_predictions),
                        "weight": round(bin_weight, 4),
                        "contribution": round(bin_ece, 4)
                    })
            
            self.current_ece = ece
            
            ece_result = {
                "ece": round(ece, 4),
                "ece_threshold": self.ece_threshold,
                "breach": ece > self.ece_threshold,
                "n_bins": n_bins,
                "total_samples": len(self.prediction_history),
                "bin_details": bin_details,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check for ECE breach
            if ece > self.ece_threshold and self.system_state == SystemState.NORMAL:
                breach_result = self._trigger_weight_lock(ece_result)
                ece_result.update(breach_result)
            
            system_logger.logger.info("ECE_CALCULATED", **ece_result)
            return ece_result
            
        except Exception as e:
            system_logger.logger.error("ECE_CALCULATION_ERROR", error=str(e))
            return {"ece": 0.0, "error": str(e)}
    
    def _trigger_weight_lock(self, ece_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger mandatory weight lock when ECE threshold is breached
        """
        from src.core.trace_logger import system_logger
        
        self.system_state = SystemState.WEIGHT_LOCK
        self.weight_lock_start = datetime.utcnow()
        
        recalibration_start = self.weight_lock_start
        
        # Log critical event
        system_logger.log_mandatory_weight_lock(
            instrument="SYSTEM_WIDE",
            ece_value=ece_data["ece"],
            ece_threshold=self.ece_threshold,
            lock_timestamp=self.weight_lock_start.isoformat(),
            recalibration_start=recalibration_start.isoformat()
        )
        
        return {
            "weight_lock_triggered": True,
            "lock_start": self.weight_lock_start.isoformat(),
            "lock_duration_hours": self.weight_lock_duration.total_seconds() / 3600,
            "recalibration_start": recalibration_start.isoformat()
        }
    
    def check_weight_lock_status(self) -> Dict[str, Any]:
        """
        Check if weight lock should be released and recalibration can begin
        """
        if self.system_state != SystemState.WEIGHT_LOCK or not self.weight_lock_start:
            return {"weight_lock_active": False}
        
        elapsed = datetime.utcnow() - self.weight_lock_start
        
        if elapsed >= self.weight_lock_duration:
            # Start recalibration
            self.system_state = SystemState.RECALIBRATION
            return {
                "weight_lock_active": False,
                "weight_lock_released": True,
                "recalibration_started": True,
                "elapsed_hours": elapsed.total_seconds() / 3600
            }
        else:
            remaining = self.weight_lock_duration - elapsed
            return {
                "weight_lock_active": True,
                "remaining_hours": remaining.total_seconds() / 3600,
                "lock_start": self.weight_lock_start.isoformat()
            }
    
    def perform_isotonic_recalibration(self) -> Dict[str, Any]:
        """
        P.1: 48-hour Isotonic Recalibration
        Retrain probability calibrator using isotonic regression
        """
        from src.core.trace_logger import system_logger
        
        if len(self.prediction_history) < self.recalibration_window:
            return {
                "recalibration_status": "insufficient_data",
                "required_samples": self.recalibration_window,
                "current_samples": len(self.prediction_history)
            }
        
        try:
            # Prepare data for recalibration
            predictions = [record["predicted_prob"] for record in self.prediction_history[-self.recalibration_window:]]
            outcomes = [record["actual_outcome"] for record in self.prediction_history[-self.recalibration_window:]]
            
            # Fit isotonic regression calibrator
            self.calibrator.fit(predictions, outcomes)
            self.calibrator_fitted = True
            
            # Test calibration improvement
            calibrated_predictions = self.calibrator.predict(predictions)
            
            # Calculate ECE before and after calibration
            ece_before = self._calculate_ece_simple(predictions, outcomes)
            ece_after = self._calculate_ece_simple(calibrated_predictions.tolist(), outcomes)
            
            # Complete recalibration
            self.system_state = SystemState.NORMAL
            
            recalibration_result = {
                "recalibration_status": "completed",
                "ece_before": round(ece_before, 4),
                "ece_after": round(ece_after, 4),
                "improvement": round(ece_before - ece_after, 4),
                "samples_used": len(predictions),
                "calibrator_fitted": True,
                "system_state": self.system_state.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            system_logger.logger.critical("ISOTONIC_RECALIBRATION_COMPLETED", **recalibration_result)
            return recalibration_result
            
        except Exception as e:
            system_logger.logger.error("RECALIBRATION_ERROR", error=str(e))
            return {"recalibration_status": "failed", "error": str(e)}
    
    def get_calibrated_probability(self, raw_probability: float) -> float:
        """
        Apply isotonic calibration to raw probability if calibrator is fitted
        """
        if self.calibrator_fitted:
            try:
                return float(self.calibrator.predict([raw_probability])[0])
            except Exception:
                return raw_probability
        return raw_probability
    
    def _calculate_ece_simple(self, predictions: List[float], outcomes: List[float], n_bins: int = 10) -> float:
        """Simple ECE calculation for recalibration assessment"""
        try:
            fraction_positives, mean_predicted_value = calibration_curve(
                outcomes, predictions, n_bins=n_bins, strategy='uniform'
            )
            
            bin_boundaries = np.linspace(0, 1, n_bins + 1)
            ece = 0.0
            
            for i in range(n_bins):
                bin_mask = (np.array(predictions) >= bin_boundaries[i]) & (np.array(predictions) < bin_boundaries[i + 1])
                if i == n_bins - 1:
                    bin_mask = (np.array(predictions) >= bin_boundaries[i]) & (np.array(predictions) <= bin_boundaries[i + 1])
                
                if np.sum(bin_mask) > 0:
                    bin_confidence = np.mean(np.array(predictions)[bin_mask])
                    bin_accuracy = np.mean(np.array(outcomes)[bin_mask])
                    bin_weight = np.sum(bin_mask) / len(predictions)
                    ece += abs(bin_accuracy - bin_confidence) * bin_weight
            
            return ece
        except Exception:
            return 0.0

class ExecutionQualityMonitor:
    """
    P.2: Execution Quality Contingency (Route Diversion)
    Monitors execution quality and triggers route diversion when degraded
    """
    
    def __init__(self):
        self.slippage_threshold = 2.0  # Max acceptable slippage in pips
        self.fill_rate_threshold = 0.95  # 95% minimum fill rate
        self.execution_delay_threshold = 5.0  # Max 5 seconds
        
        self.execution_history = []
        self.route_diversion_active = False
        self.primary_route = "oanda_api"
        self.backup_routes = ["backup_broker", "internal_crossing"]
    
    def record_execution(self, execution_data: Dict[str, Any]):
        """
        Record execution data for quality monitoring
        """
        from src.core.trace_logger import system_logger
        
        execution_record = {
            "timestamp": datetime.utcnow(),
            "route": execution_data.get("route", self.primary_route),
            "slippage_pips": execution_data.get("slippage_pips", 0.0),
            "fill_rate": execution_data.get("fill_rate", 1.0),
            "execution_delay_seconds": execution_data.get("execution_delay", 0.0),
            "success": execution_data.get("success", True),
            "instrument": execution_data.get("instrument", "UNKNOWN")
        }
        
        self.execution_history.append(execution_record)
        
        # Limit history for performance
        if len(self.execution_history) > 500:
            self.execution_history = self.execution_history[-500:]
        
        system_logger.logger.debug("EXECUTION_RECORDED", **execution_record)
    
    def assess_execution_quality(self, lookback_minutes: int = 30) -> Dict[str, Any]:
        """
        Assess recent execution quality and determine if route diversion needed
        """
        from src.core.trace_logger import system_logger
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        recent_executions = [
            record for record in self.execution_history 
            if record["timestamp"] >= cutoff_time
        ]
        
        if len(recent_executions) < 5:  # Minimum sample size
            return {
                "quality_assessment": "insufficient_data",
                "sample_count": len(recent_executions)
            }
        
        # Calculate quality metrics
        avg_slippage = np.mean([record["slippage_pips"] for record in recent_executions])
        avg_fill_rate = np.mean([record["fill_rate"] for record in recent_executions])
        avg_delay = np.mean([record["execution_delay_seconds"] for record in recent_executions])
        success_rate = np.mean([1.0 if record["success"] else 0.0 for record in recent_executions])
        
        # Quality degradation checks
        quality_issues = []
        if avg_slippage > self.slippage_threshold:
            quality_issues.append(f"high_slippage_{avg_slippage:.2f}_pips")
        
        if avg_fill_rate < self.fill_rate_threshold:
            quality_issues.append(f"low_fill_rate_{avg_fill_rate:.2%}")
        
        if avg_delay > self.execution_delay_threshold:
            quality_issues.append(f"high_delay_{avg_delay:.1f}s")
        
        if success_rate < 0.9:
            quality_issues.append(f"low_success_rate_{success_rate:.2%}")
        
        # Determine if route diversion needed
        diversion_needed = len(quality_issues) >= 2  # Multiple quality issues
        
        quality_result = {
            "lookback_minutes": lookback_minutes,
            "sample_count": len(recent_executions),
            "avg_slippage_pips": round(avg_slippage, 2),
            "avg_fill_rate": round(avg_fill_rate, 4),
            "avg_delay_seconds": round(avg_delay, 2),
            "success_rate": round(success_rate, 4),
            "quality_issues": quality_issues,
            "diversion_needed": diversion_needed,
            "current_route": self.primary_route,
            "route_diversion_active": self.route_diversion_active,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Trigger route diversion if needed
        if diversion_needed and not self.route_diversion_active:
            diversion_result = self._trigger_route_diversion(quality_result)
            quality_result.update(diversion_result)
        
        system_logger.logger.info("EXECUTION_QUALITY_ASSESSED", **quality_result)
        return quality_result
    
    def _trigger_route_diversion(self, quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        P.2: Trigger route diversion to backup execution venues
        """
        from src.core.trace_logger import system_logger
        
        self.route_diversion_active = True
        selected_backup = self.backup_routes[0]  # Select first available backup
        
        diversion_result = {
            "route_diversion_triggered": True,
            "previous_route": self.primary_route,
            "diverted_to": selected_backup,
            "trigger_reason": quality_data["quality_issues"],
            "diversion_timestamp": datetime.utcnow().isoformat()
        }
        
        system_logger.logger.critical("ROUTE_DIVERSION_TRIGGERED", **diversion_result)
        return diversion_result
    
    def get_current_route(self) -> str:
        """Get current execution route (primary or diverted)"""
        if self.route_diversion_active:
            return self.backup_routes[0]
        return self.primary_route
    
    def reset_route_diversion(self):
        """Reset route diversion (typically after manual intervention)"""
        from src.core.trace_logger import system_logger
        
        self.route_diversion_active = False
        system_logger.logger.info("ROUTE_DIVERSION_RESET", 
                                route=self.primary_route,
                                timestamp=datetime.utcnow().isoformat())

# Global instances
calibration_auditor = CalibrationDegradationAuditor()
execution_monitor = ExecutionQualityMonitor()