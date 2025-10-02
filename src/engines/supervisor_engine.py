"""
System 2.1: Enhanced Supervisor Engine with GSSI/CAR Integration
Implements decision audit logging and regime-aware weight management
"""

from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import asyncio

from .engine_base import EngineBase

class SupervisorEngine(EngineBase):
    """
    Enhanced Supervisor Engine for System 2.1
    Integrates GSSI/CAR, MRC regime weights, and Sentinel overrides
    """
    
    def __init__(self, engines, weights):
        self.engines = engines
        self.base_weights = weights
        self.current_weights = weights.copy()
        
        # System 2.1 integrations
        self.gssi_car_integration = True
        self.mrc_integration = True
        self.sentinel_integration = True
        
    def score(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Enhanced scoring with System 2.1 integrations
        Implements L.2: Decision Audit logging
        """
        # Run async scoring in event loop
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create task if in running loop
                task = asyncio.create_task(self._async_score(context))
                return loop.run_until_complete(task)
            else:
                return asyncio.run(self._async_score(context))
        except Exception as e:
            # Fallback to basic scoring
            return self._basic_score(context)
    
    def _basic_score(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Fallback basic scoring without async features"""
        scores = {}
        reasons = {}
        
        for name, engine in self.engines.items():
            try:
                result = engine.score(context)
                if isinstance(result, tuple) and len(result) == 2:
                    score, reason = result
                elif isinstance(result, (int, float)):
                    score, reason = float(result), "numeric_result"
                else:
                    score, reason = 0.0, "unknown_result_type"
                
                scores[name] = score
                reasons[name] = reason
            except Exception as e:
                scores[name] = 0.0
                reasons[name] = f"error: {str(e)}"
        
        final_score = sum(scores[name] * self.current_weights.get(name, 0.0) for name in scores)
        
        return final_score, {
            "supervisor_decision": "BASIC_FALLBACK",
            "final_score": final_score,
            "engine_scores": scores,
            "reasons": reasons
        }
    
    async def _async_score(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Enhanced scoring with System 2.1 integrations
        Implements L.2: Decision Audit logging
        """
        from src.core.trace_logger import system_logger, TraceContext
        from src.engines.gssi_car_engine import gssi_car_engine, market_regime_classifier
        from src.engines.sentinel_engine import sentinel_engine
        
        # Check for Sentinel override first
        if sentinel_engine.should_override_strategy_router():
            sentinel_status = sentinel_engine.get_current_status()
            override_result = {
                "supervisor_decision": "SENTINEL_OVERRIDE",
                "sentinel_mode": sentinel_status["mode"],
                "override_reason": "black_swan_protection",
                "final_score": 0.0,  # Block normal trading
                "engine_scores": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            system_logger.log_supervisor_decision(
                instrument=context.get("instrument", "UNKNOWN"),
                input_scores={},
                output_decision=override_result
            )
            
            return 0.0, override_result
        
        # Get MRC regime weights if enabled
        if self.mrc_integration:
            regime_weights = market_regime_classifier.get_current_weight_profile()
            self.current_weights = self._merge_weights(self.base_weights, regime_weights)
        
        # Aggregate engine scores using current weights
        scores = {}
        reasons = {}
        engine_details = {}
        
        for name, engine in self.engines.items():
            try:
                if hasattr(engine, 'score') and callable(engine.score):
                    if asyncio.iscoroutinefunction(engine.score):
                        result = await engine.score(context)
                    else:
                        result = engine.score(context)
                    
                    # Handle result unpacking safely
                    if isinstance(result, tuple) and len(result) == 2:
                        score, reason = result
                    elif isinstance(result, (int, float)):
                        score, reason = float(result), "numeric_result"
                    else:
                        score, reason = 0.0, "unknown_result_type"
                else:
                    score, reason = 0.0, "engine_not_callable"
                
                scores[name] = score
                reasons[name] = reason
                engine_details[name] = {
                    "score": round(score, 4),
                    "weight": self.current_weights.get(name, 0.0),
                    "weighted_contribution": round(score * self.current_weights.get(name, 0.0), 4),
                    "reason": reason
                }
                
            except Exception as e:
                scores[name] = 0.0
                reasons[name] = f"engine_error: {str(e)}"
                engine_details[name] = {
                    "score": 0.0,
                    "weight": 0.0,
                    "weighted_contribution": 0.0,
                    "error": str(e)
                }
        
        # Calculate weighted final score
        final_score = sum(scores[name] * self.current_weights.get(name, 0.0) for name in scores)
        
        # Apply GSSI/CAR adjustments if enabled
        if self.gssi_car_integration:
            gssi_adjustment = await self._apply_gssi_car_adjustment(final_score, context)
            final_score = gssi_adjustment["adjusted_score"]
        else:
            gssi_adjustment = {"applied": False}
        
        # Build comprehensive decision record
        decision_result = {
            "supervisor_decision": "NORMAL_PROCESSING",
            "final_score": round(final_score, 4),
            "engine_scores": scores,
            "engine_details": engine_details,
            "weights_used": self.current_weights,
            "regime_weights_applied": self.mrc_integration,
            "gssi_car_adjustment": gssi_adjustment,
            "sentinel_override": False,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": TraceContext.get_trace_id()
        }
        
        # L.2: Log complete supervisor decision audit
        system_logger.log_supervisor_decision(
            instrument=context.get("instrument", "UNKNOWN"),
            input_scores=scores,
            output_decision=decision_result
        )
        
        return final_score, decision_result
    
    async def _apply_gssi_car_adjustment(self, base_score: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply GSSI/CAR risk adjustment to supervisor score
        """
        from src.engines.gssi_car_engine import gssi_car_engine
        
        try:
            # Calculate GSSI score from market context
            market_data = context.get("market_data", {})
            gssi_result = gssi_car_engine.calculate_gssi_score(market_data)
            gssi_score = gssi_result["gssi_score"]
            
            # Calculate CAR score from portfolio context
            portfolio_data = context.get("portfolio_data", {})
            car_result = gssi_car_engine.calculate_car_score(portfolio_data, gssi_score)
            car_score = car_result["car_score"]
            
            # Apply score adjustment based on stress levels
            if gssi_score >= 0.8 or car_score >= 0.7:
                adjustment_factor = 0.3  # Reduce score by 70%
            elif gssi_score >= 0.6 or car_score >= 0.5:
                adjustment_factor = 0.6  # Reduce score by 40%
            elif gssi_score >= 0.4 or car_score >= 0.3:
                adjustment_factor = 0.8  # Reduce score by 20%
            else:
                adjustment_factor = 1.0  # No adjustment
            
            adjusted_score = base_score * adjustment_factor
            
            return {
                "applied": True,
                "gssi_score": gssi_score,
                "car_score": car_score,
                "adjustment_factor": adjustment_factor,
                "base_score": base_score,
                "adjusted_score": adjusted_score,
                "reduction_pct": round((1 - adjustment_factor) * 100, 1)
            }
            
        except Exception as e:
            return {
                "applied": False,
                "error": str(e),
                "base_score": base_score,
                "adjusted_score": base_score
            }
    
    def _merge_weights(self, base_weights: Dict[str, float], 
                      regime_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Merge base weights with regime-specific weights
        Regime weights take precedence where available
        """
        merged = base_weights.copy()
        
        # Update with regime weights
        for engine_name, regime_weight in regime_weights.items():
            if engine_name in merged:
                merged[engine_name] = regime_weight
        
        # Normalize weights to sum to 1.0
        total_weight = sum(merged.values())
        if total_weight > 0:
            merged = {name: weight / total_weight for name, weight in merged.items()}
        
        return merged
    
    def update_base_weights(self, new_weights: Dict[str, float]):
        """Update base engine weights"""
        self.base_weights = new_weights.copy()
        if not self.mrc_integration:
            self.current_weights = new_weights.copy()
    
    def get_current_weights(self) -> Dict[str, float]:
        """Get currently active weights"""
        return self.current_weights.copy()
    
    def get_weight_history(self) -> Dict[str, Any]:
        """Get weight configuration history for debugging"""
        return {
            "base_weights": self.base_weights,
            "current_weights": self.current_weights,
            "mrc_integration": self.mrc_integration,
            "gssi_car_integration": self.gssi_car_integration,
            "sentinel_integration": self.sentinel_integration
        }
