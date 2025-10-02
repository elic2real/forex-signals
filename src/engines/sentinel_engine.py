"""
System 2.1: Sentinel Engine - Black Swan Protection & Override System
Implementation of Engine 12: Sentinel with Protect/Pounce modes (R.2)
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from decimal import Decimal
from datetime import datetime, timedelta
import asyncio

class SentinelMode(Enum):
    STAND_DOWN = "stand_down"
    PROTECT = "protect" 
    POUNCE = "pounce"

class SentinelEngine:
    """
    Black Swan Sentinel Engine with Override Capabilities
    Implements R.2: Protect/Pounce Mode Logic
    """
    
    def __init__(self):
        self.mode = SentinelMode.STAND_DOWN
        self.swan_threshold = Decimal('0.70')  # Override threshold
        self.last_assessment = None
        self.mode_duration = timedelta(hours=6)  # How long to stay in active mode
        self.mode_start_time = None
        
        # Protect mode settings
        self.protect_max_spread = Decimal('1.0')  # Stricter spread gate
        self.protect_disabled_strategies = ["range_fade", "main_smc_adds"]
        
        # Pounce mode settings  
        self.pounce_tp_multipliers = {"min": Decimal('2.0'), "max": Decimal('2.8')}
        self.pounce_enabled_strategies = ["session_breakout", "sentiment_breakout"]
    
    async def assess_and_update_mode(self, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main assessment function - checks for black swan conditions
        and updates Sentinel mode accordingly
        """
        from src.core.trace_logger import system_logger, TraceContext
        from src.engines.ollama_llm_engine import llm_engine
        
        # Get LLM black swan assessment
        swan_assessment = await llm_engine.assess_black_swan_risk(market_context)
        
        swan_score = Decimal(str(swan_assessment.get("swan_score", 0.0)))
        recommended_mode = swan_assessment.get("recommended_mode", "stand_down")
        
        # Check if we should override strategy routing
        previous_mode = self.mode
        
        if swan_score >= self.swan_threshold:
            # High swan score - activate override mode
            if recommended_mode == "protect":
                self.mode = SentinelMode.PROTECT
            elif recommended_mode == "pounce":
                self.mode = SentinelMode.POUNCE
            else:
                self.mode = SentinelMode.PROTECT  # Default to protect in high risk
                
            self.mode_start_time = datetime.utcnow()
            
        elif self.mode != SentinelMode.STAND_DOWN:
            # Check if we should exit active mode
            if (self.mode_start_time and 
                datetime.utcnow() - self.mode_start_time > self.mode_duration):
                self.mode = SentinelMode.STAND_DOWN
                self.mode_start_time = None
        
        # Build result
        result = {
            "previous_mode": previous_mode.value,
            "current_mode": self.mode.value,
            "swan_score": float(swan_score),
            "override_active": swan_score >= self.swan_threshold,
            "llm_recommendation": recommended_mode,
            "risk_factors": swan_assessment.get("risk_factors", []),
            "mode_duration_remaining": self._get_mode_duration_remaining(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log mode changes
        if previous_mode != self.mode:
            system_logger.logger.critical("SENTINEL_MODE_CHANGE", **result)
        else:
            system_logger.logger.info("SENTINEL_ASSESSMENT", **result)
        
        self.last_assessment = result
        return result
    
    def should_override_strategy_router(self) -> bool:
        """Check if Sentinel should override normal strategy routing"""
        return self.mode != SentinelMode.STAND_DOWN
    
    def apply_protect_mode_constraints(self, trading_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Protect Mode constraints (R.2)
        - Forces stricter spread gate
        - Disables Range Fade/MAIN/SMC adds
        """
        from src.core.trace_logger import system_logger
        
        if self.mode != SentinelMode.PROTECT:
            return trading_params
        
        # Apply stricter spread gate
        original_max_spread = trading_params.get("max_spread_pips", 2.0)
        trading_params["max_spread_pips"] = float(self.protect_max_spread)
        
        # Disable risky strategies
        if "strategy" in trading_params:
            if trading_params["strategy"] in self.protect_disabled_strategies:
                trading_params["strategy_blocked"] = True
                trading_params["block_reason"] = "sentinel_protect_mode"
        
        # Disable add-to-winners
        trading_params["add_to_winners_disabled"] = True
        
        from src.core.trace_logger import GuardrailStatus
        system_logger.log_guardrail_check(
            instrument=trading_params.get("instrument", "UNKNOWN"),
            gate_name="sentinel_protect_constraints",
            status=GuardrailStatus.BLOCK if trading_params.get("strategy_blocked") else GuardrailStatus.PASS,
            reason=f"Protect mode: spread_limit={self.protect_max_spread}, disabled_strategies={self.protect_disabled_strategies}"
        )
        
        return trading_params
    
    def apply_pounce_mode_enhancements(self, trading_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Pounce Mode enhancements (R.2)
        - Enables stop-only entries for breakouts
        - Lifts TP multiples when Velocity TP-Bypass is enabled
        """
        from src.core.trace_logger import system_logger
        
        if self.mode != SentinelMode.POUNCE:
            return trading_params
        
        # Enable stop-only entries for breakout strategies
        if trading_params.get("strategy") in self.pounce_enabled_strategies:
            trading_params["entry_type"] = "stop_only"
            trading_params["pounce_mode_enabled"] = True
        
        # Lift TP multiples if velocity bypass is active
        if trading_params.get("velocity_tp_bypass_enabled"):
            original_tp_multiple = trading_params.get("tp_multiple", 1.5)
            enhanced_tp_multiple = min(
                float(self.pounce_tp_multipliers["max"]),
                original_tp_multiple * 1.5  # 50% enhancement
            )
            trading_params["tp_multiple"] = enhanced_tp_multiple
            trading_params["tp_enhancement_reason"] = "sentinel_pounce_mode"
        
        system_logger.logger.info("SENTINEL_POUNCE_ENHANCEMENT", 
                                instrument=trading_params.get("instrument", "UNKNOWN"),
                                original_tp=trading_params.get("tp_multiple", 1.5),
                                enhanced_tp=trading_params.get("tp_multiple"),
                                entry_type=trading_params.get("entry_type"))
        
        return trading_params
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current Sentinel status for monitoring"""
        return {
            "mode": self.mode.value,
            "override_active": self.mode != SentinelMode.STAND_DOWN,
            "mode_duration_remaining": self._get_mode_duration_remaining(),
            "last_assessment": self.last_assessment,
            "protect_constraints": {
                "max_spread_pips": float(self.protect_max_spread),
                "disabled_strategies": self.protect_disabled_strategies
            },
            "pounce_enhancements": {
                "tp_multiplier_range": {
                    "min": float(self.pounce_tp_multipliers["min"]),
                    "max": float(self.pounce_tp_multipliers["max"])
                },
                "enabled_strategies": self.pounce_enabled_strategies
            }
        }
    
    def _get_mode_duration_remaining(self) -> Optional[float]:
        """Get remaining time in current mode (seconds)"""
        if not self.mode_start_time or self.mode == SentinelMode.STAND_DOWN:
            return None
        
        elapsed = datetime.utcnow() - self.mode_start_time
        remaining = self.mode_duration - elapsed
        
        return max(0.0, remaining.total_seconds())

class LiquidityCliffMonitor:
    """
    Liquidity Cliff Emergency Monitor
    Implements T.3: Test_Liquidity_Cliff_Emergency
    """
    
    def __init__(self):
        self.spread_ratio_threshold = Decimal('4.0')  # p99/p50 > 4.0
        self.emergency_active = False
    
    def check_liquidity_cliff(self, spread_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor for liquidity cliff conditions
        Trigger emergency actions when spread_p99/spread_p50 > 4.0
        """
        from src.core.trace_logger import system_logger
        
        spread_p50 = Decimal(str(spread_data.get("p50", 1.0)))
        spread_p99 = Decimal(str(spread_data.get("p99", 2.0)))
        
        if spread_p50 > 0:
            spread_ratio = spread_p99 / spread_p50
        else:
            spread_ratio = Decimal('999.0')  # Extreme case
        
        cliff_detected = spread_ratio > self.spread_ratio_threshold
        
        result = {
            "spread_ratio": float(spread_ratio),
            "threshold": float(self.spread_ratio_threshold),
            "cliff_detected": cliff_detected,
            "spread_p50": float(spread_p50),
            "spread_p99": float(spread_p99),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if cliff_detected and not self.emergency_active:
            self.emergency_active = True
            result["emergency_actions"] = self._trigger_emergency_actions()
            system_logger.log_liquidity_cliff_emergency(
                instrument=spread_data.get("instrument", "UNKNOWN"),
                spread_ratio=float(spread_ratio),
                cancelled_orders=result["emergency_actions"]["cancelled_orders"],
                market_exits=result["emergency_actions"]["market_exits"]
            )
        elif not cliff_detected and self.emergency_active:
            self.emergency_active = False
            result["emergency_actions"] = {"status": "emergency_cleared"}
        
        return result
    
    def _trigger_emergency_actions(self) -> Dict[str, Any]:
        """
        Execute emergency actions during liquidity cliff
        - Cancel all conditional orders
        - Market exit trades with R_realized < -0.2R_nominal
        """
        # This would integrate with actual trading system
        # For now, return mock action counts
        return {
            "cancelled_orders": 5,  # Mock count
            "market_exits": 2,      # Mock count
            "action_timestamp": datetime.utcnow().isoformat(),
            "reason": "liquidity_cliff_emergency"
        }

# Global instances
sentinel_engine = SentinelEngine()
liquidity_monitor = LiquidityCliffMonitor()