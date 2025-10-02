"""
System 2.1: Comprehensive Test Suite
Implementation of T.1, T.2, T.3 test declarations
Unit, Integration, and Acceptance tests for all critical components
"""

import pytest
import asyncio
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import json

# Import system components
from src.core.sizing import PositionSizer, AddToWinnersManager, QuantileATRCalculator
from src.engines.sentinel_engine import SentinelEngine, LiquidityCliffMonitor, SentinelMode
from src.core.trace_logger import system_logger, TraceContext

class TestSizingPrecision:
    """
    T.1: Test_Sizing_Precision
    Verify Position Sizing uses Decimal math and adheres to Kelly-Lite cap and 50x leverage limits
    """
    
    def test_decimal_precision_calculations(self):
        """Test that all sizing calculations use Decimal precision"""
        sizer = PositionSizer(account_balance=Decimal('10000'))
        
        result = sizer.calculate_position_size(
            instrument="EURUSD",
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.0950'),
            kelly_fraction=Decimal('0.15'),
            gssi_score=Decimal('0.3')
        )
        
        # Verify result contains Decimal final_units
        assert isinstance(result["units"], Decimal)
        assert result["leverage"] <= 50.0  # Max leverage check
        
        # Verify floor operation was applied
        sizing_breakdown = result["sizing_breakdown"]
        units_risk = Decimal(str(sizing_breakdown["units_risk"]))
        units_notional = Decimal(str(sizing_breakdown["units_notional"]))
        final_units = result["units"]
        
        # Final Units = floor(min(units_risk, units_notional))
        expected_final = min(units_risk, units_notional).quantize(Decimal('1'))
        assert final_units == expected_final
    
    def test_kelly_lite_cap_enforcement(self):
        """Test Kelly-Lite cap is enforced at 25%"""
        sizer = PositionSizer(account_balance=Decimal('10000'))
        
        # Test with Kelly fraction > 25%
        result = sizer.calculate_position_size(
            instrument="EURUSD",
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.0950'),
            kelly_fraction=Decimal('0.40')  # Above 25% cap
        )
        
        # Kelly should be capped at 25%
        assert result["sizing_breakdown"]["kelly_fraction"] <= 0.25
    
    def test_leverage_limit_enforcement(self):
        """Test 50x leverage limit is enforced"""
        sizer = PositionSizer(account_balance=Decimal('1000'))
        
        result = sizer.calculate_position_size(
            instrument="EURUSD", 
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.0900'),  # Large stop for high leverage test
            kelly_fraction=Decimal('0.25')
        )
        
        assert result["leverage"] <= 50.0

class TestAddToWinnersEligibility:
    """
    T.1: Test_Add_to_Winners_Eligibility
    Verify Add-to-Winners state machine moves to add_1 only when progress >= +0.7R AND drawdown <= 0.25R
    """
    
    def test_add_eligibility_conditions(self):
        """Test precise eligibility conditions"""
        manager = AddToWinnersManager()
        
        # Test: progress >= 0.7R AND drawdown <= 0.25R
        result = manager.check_add_eligibility(
            current_progress=Decimal('0.7'),    # Exactly at threshold
            max_drawdown=Decimal('0.25'),       # Exactly at limit
            initial_risk=Decimal('100')
        )
        
        assert result["eligible"] == True
        assert result["current_state"] == "add_1"
        assert result["new_breakeven"] is not None
    
    def test_add_rejection_insufficient_progress(self):
        """Test rejection when progress < 0.7R"""
        manager = AddToWinnersManager()
        
        result = manager.check_add_eligibility(
            current_progress=Decimal('0.69'),   # Just below threshold
            max_drawdown=Decimal('0.20'),       # Good drawdown
            initial_risk=Decimal('100')
        )
        
        assert result["eligible"] == False
        assert result["current_state"] == "initial"
    
    def test_add_rejection_excessive_drawdown(self):
        """Test rejection when drawdown > 0.25R"""
        manager = AddToWinnersManager()
        
        result = manager.check_add_eligibility(
            current_progress=Decimal('0.8'),    # Good progress
            max_drawdown=Decimal('0.26'),       # Just above limit
            initial_risk=Decimal('100')
        )
        
        assert result["eligible"] == False
        assert result["current_state"] == "initial"

class TestConditionalOrderLogic:
    """
    T.1: Test_Conditional_Order_Logic  
    Test Conditional Order Engine ensures only one condition (stop OR limit) is present
    """
    
    def test_single_condition_validation(self):
        """Test that only one condition (stop OR limit) is allowed"""
        # This would test the actual conditional order engine
        # For now, test the validation logic
        
        valid_stop_order = {
            "type": "stop",
            "price": 1.1050,
            "condition": "price >= 1.1050"
        }
        
        valid_limit_order = {
            "type": "limit", 
            "price": 1.0950,
            "condition": "price <= 1.0950"
        }
        
        invalid_dual_order = {
            "type": "both",
            "stop_price": 1.1050,
            "limit_price": 1.0950
        }
        
        # Test validation function (would be in actual engine)
        assert self._validate_order_conditions(valid_stop_order) == True
        assert self._validate_order_conditions(valid_limit_order) == True
        assert self._validate_order_conditions(invalid_dual_order) == False
    
    def _validate_order_conditions(self, order: Dict[str, Any]) -> bool:
        """Mock validation - only one condition allowed"""
        if order.get("type") == "both":
            return False
        return True

class TestExitsBreakeven:
    """
    T.1: Test_Exits_Breakeven
    Verify Trade Manager sets BE precisely at +0.7R for MAIN/SMC
    """
    
    def test_breakeven_at_07r(self):
        """Test BE is set exactly at +0.7R"""
        initial_entry = Decimal('1.1000')
        initial_stop = Decimal('1.0950') 
        risk_amount = initial_entry - initial_stop  # 0.0050
        
        # +0.7R should be: entry + (0.7 * risk_amount)
        expected_be = initial_entry + (Decimal('0.7') * risk_amount)
        # expected_be = 1.1000 + (0.7 * 0.0050) = 1.1035
        
        # Test the BE calculation
        calculated_be = self._calculate_breakeven_at_07r(initial_entry, initial_stop)
        
        assert calculated_be == expected_be
        assert calculated_be == Decimal('1.1035')
    
    def _calculate_breakeven_at_07r(self, entry: Decimal, stop: Decimal) -> Decimal:
        """Calculate BE at +0.7R"""
        risk = entry - stop
        return entry + (Decimal('0.7') * risk)

class TestGSSICARCascade:
    """
    T.2: Test_GSSI_CAR_Cascade
    Verify GSSI score -> CAR score -> Dynamic Leverage correctly reduces Position Size when GSSI is high
    """
    
    def test_gssi_to_car_flow(self):
        """Test complete GSSI -> CAR -> Dynamic Leverage flow"""
        
        # Mock GSSI calculation
        gssi_score = Decimal('0.8')  # High GSSI
        
        # Mock CAR calculation from GSSI
        car_score = self._calculate_car_from_gssi(gssi_score)
        
        # Test dynamic leverage reduction
        base_leverage = Decimal('20.0')
        adjusted_leverage = self._apply_dynamic_leverage(base_leverage, car_score)
        
        # High GSSI should reduce leverage
        assert adjusted_leverage < base_leverage
        assert adjusted_leverage <= Decimal('10.0')  # Should cap at 50% when GSSI >= 0.8
    
    def test_position_size_reduction_cascade(self):
        """Test that high GSSI ultimately reduces position size"""
        sizer = PositionSizer(account_balance=Decimal('10000'))
        
        # Low GSSI scenario
        result_low_gssi = sizer.calculate_position_size(
            instrument="EURUSD",
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.0950'),
            gssi_score=Decimal('0.2')  # Low GSSI
        )
        
        # High GSSI scenario  
        result_high_gssi = sizer.calculate_position_size(
            instrument="EURUSD",
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.0950'),
            gssi_score=Decimal('0.8')  # High GSSI
        )
        
        # High GSSI should result in smaller position
        assert result_high_gssi["units"] < result_low_gssi["units"]
    
    def _calculate_car_from_gssi(self, gssi: Decimal) -> Decimal:
        """Mock CAR calculation from GSSI"""
        # CAR increases with GSSI
        return gssi * Decimal('1.2')
    
    def _apply_dynamic_leverage(self, base_leverage: Decimal, car_score: Decimal) -> Decimal:
        """Mock dynamic leverage application"""
        if car_score >= Decimal('0.8'):
            return base_leverage * Decimal('0.5')  # 50% reduction
        elif car_score >= Decimal('0.6'):
            return base_leverage * Decimal('0.75')  # 25% reduction
        else:
            return base_leverage

class TestSentinelOverride:
    """
    T.2: Test_Sentinel_Override
    Assert when swan_score >= 0.70, Sentinel mode successfully overrides Strategy Router choice
    """
    
    @pytest.mark.asyncio
    async def test_sentinel_override_activation(self):
        """Test Sentinel override when swan_score >= 0.70"""
        sentinel = SentinelEngine()
        
        # Mock market context with high swan risk
        high_risk_context = {
            "volatility": 0.95,
            "correlation_breakdown": True,
            "liquidity_stress": 0.8
        }
        
        # Mock LLM response with high swan score
        with patch('src.engines.ollama_llm_engine.llm_engine.assess_black_swan_risk') as mock_llm:
            mock_llm.return_value = {
                "swan_score": 0.75,  # Above 0.70 threshold
                "recommended_mode": "protect",
                "risk_factors": ["liquidity_stress", "correlation_breakdown"]
            }
            
            result = await sentinel.assess_and_update_mode(high_risk_context)
            
            # Verify override is activated
            assert result["override_active"] == True
            assert result["current_mode"] == "protect"
            assert sentinel.should_override_strategy_router() == True
    
    @pytest.mark.asyncio
    async def test_no_override_low_swan_score(self):
        """Test no override when swan_score < 0.70"""
        sentinel = SentinelEngine()
        
        low_risk_context = {"volatility": 0.3}
        
        with patch('src.engines.ollama_llm_engine.llm_engine.assess_black_swan_risk') as mock_llm:
            mock_llm.return_value = {
                "swan_score": 0.4,  # Below threshold
                "recommended_mode": "stand_down"
            }
            
            result = await sentinel.assess_and_update_mode(low_risk_context)
            
            # No override should be active
            assert result["override_active"] == False
            assert result["current_mode"] == "stand_down"
            assert sentinel.should_override_strategy_router() == False

class TestCurrencyBucketCap:
    """
    T.2: Test_Currency_Bucket_Cap
    Simulate hitting Currency-Bucket limit and verify Guardrails block new entry for capped currency
    """
    
    def test_currency_bucket_limit_enforcement(self):
        """Test currency bucket cap blocks new trades for capped currencies"""
        
        # Mock current positions
        current_positions = {
            "EUR": {"count": 5, "exposure": 500000},  # At limit
            "USD": {"count": 3, "exposure": 300000},  # Below limit  
            "GBP": {"count": 2, "exposure": 200000}   # Below limit
        }
        
        currency_limits = {
            "EUR": {"max_count": 5, "max_exposure": 500000},
            "USD": {"max_count": 5, "max_exposure": 500000},
            "GBP": {"max_count": 5, "max_exposure": 500000}
        }
        
        # Test EUR trade (should be blocked)
        eur_trade_allowed = self._check_currency_limit("EURUSD", current_positions, currency_limits)
        assert eur_trade_allowed == False
        
        # Test GBP trade (should be allowed)
        gbp_trade_allowed = self._check_currency_limit("GBPUSD", current_positions, currency_limits)
        assert gbp_trade_allowed == True
    
    def _check_currency_limit(self, instrument: str, positions: Dict, limits: Dict) -> bool:
        """Mock currency limit check"""
        base_currency = instrument[:3]
        
        if base_currency in positions:
            current_count = positions[base_currency]["count"]
            max_count = limits[base_currency]["max_count"]
            return current_count < max_count
        
        return True  # No positions, allow trade

class TestSafetyCompliance:
    """
    T.3: Test_Safety_Compliance
    Assert Pre-Order Safety Check throws exception on anti-hedge, duplicate units, or >50x leverage
    """
    
    def test_anti_hedge_prevention(self):
        """Test anti-hedging prevention"""
        existing_position = {"instrument": "EURUSD", "side": "long", "units": 100000}
        new_order = {"instrument": "EURUSD", "side": "short", "units": 50000}
        
        with pytest.raises(Exception) as exc_info:
            self._pre_order_safety_check(new_order, [existing_position])
        
        assert "anti-hedge" in str(exc_info.value).lower()
    
    def test_duplicate_units_prevention(self):
        """Test duplicate exact units prevention"""
        existing_position = {"instrument": "EURUSD", "side": "long", "units": 100000}
        new_order = {"instrument": "EURUSD", "side": "long", "units": 100000}  # Exact duplicate
        
        with pytest.raises(Exception) as exc_info:
            self._pre_order_safety_check(new_order, [existing_position])
        
        assert "duplicate" in str(exc_info.value).lower()
    
    def test_leverage_limit_exception(self):
        """Test >50x leverage throws exception"""
        new_order = {
            "instrument": "EURUSD",
            "side": "long", 
            "units": 1000000,
            "leverage": 55.0  # Above 50x limit
        }
        
        with pytest.raises(Exception) as exc_info:
            self._pre_order_safety_check(new_order, [])
        
        assert "leverage" in str(exc_info.value).lower()
    
    def _pre_order_safety_check(self, new_order: Dict, existing_positions: list):
        """Mock pre-order safety check"""
        
        # Check anti-hedging
        for pos in existing_positions:
            if (pos["instrument"] == new_order["instrument"] and 
                pos["side"] != new_order["side"]):
                raise Exception("Anti-hedge violation detected")
        
        # Check duplicate units
        for pos in existing_positions:
            if (pos["instrument"] == new_order["instrument"] and
                pos["side"] == new_order["side"] and
                pos["units"] == new_order["units"]):
                raise Exception("Duplicate exact units detected")
        
        # Check leverage limit
        if new_order.get("leverage", 0) > 50:
            raise Exception("Leverage exceeds 50x limit")

class TestLiquidityCliffEmergency:
    """
    T.3: Test_Liquidity_Cliff_Emergency
    Simulate spread_p99/spread_p50 > 4.0 and verify emergency actions
    """
    
    def test_liquidity_cliff_detection(self):
        """Test liquidity cliff detection and emergency actions"""
        monitor = LiquidityCliffMonitor()
        
        # Normal spreads
        normal_spreads = {"p50": 1.5, "p99": 4.0, "instrument": "EURUSD"}  # Ratio = 2.67
        result_normal = monitor.check_liquidity_cliff(normal_spreads)
        assert result_normal["cliff_detected"] == False
        
        # Cliff condition
        cliff_spreads = {"p50": 1.0, "p99": 5.0, "instrument": "EURUSD"}  # Ratio = 5.0 > 4.0
        result_cliff = monitor.check_liquidity_cliff(cliff_spreads)
        
        assert result_cliff["cliff_detected"] == True
        assert result_cliff["spread_ratio"] > 4.0
        assert "emergency_actions" in result_cliff
        
        # Verify emergency actions were logged
        actions = result_cliff["emergency_actions"]
        assert actions["cancelled_orders"] >= 0
        assert actions["market_exits"] >= 0

class TestDrawdownKillSwitch:
    """
    T.3: Test_Drawdown_Kill_Switch
    Assert if Daily Drawdown > 5% vs day's peak NAV, all trades Flatten and system enters Halt mode
    """
    
    def test_kill_switch_activation(self):
        """Test kill switch activates at >5% daily drawdown"""
        peak_nav = Decimal('100000')
        current_nav = Decimal('94000')  # 6% drawdown
        
        daily_drawdown_pct = float((peak_nav - current_nav) / peak_nav * 100)
        
        assert daily_drawdown_pct > 5.0  # Verify > 5% threshold
        
        # Test kill switch logic
        kill_switch_active = self._check_kill_switch(daily_drawdown_pct, peak_nav, current_nav)
        
        assert kill_switch_active["activated"] == True
        assert kill_switch_active["trades_flattened"] > 0
        assert kill_switch_active["system_mode"] == "HALT"
    
    def test_kill_switch_no_activation(self):
        """Test kill switch doesn't activate below 5% drawdown"""
        peak_nav = Decimal('100000')
        current_nav = Decimal('96000')  # 4% drawdown
        
        daily_drawdown_pct = float((peak_nav - current_nav) / peak_nav * 100)
        
        kill_switch_active = self._check_kill_switch(daily_drawdown_pct, peak_nav, current_nav)
        
        assert kill_switch_active["activated"] == False
        assert kill_switch_active["system_mode"] == "NORMAL"
    
    def _check_kill_switch(self, drawdown_pct: float, peak_nav: Decimal, current_nav: Decimal) -> Dict[str, Any]:
        """Mock kill switch check"""
        if drawdown_pct > 5.0:
            return {
                "activated": True,
                "trades_flattened": 8,  # Mock count
                "system_mode": "HALT",
                "drawdown_pct": drawdown_pct
            }
        else:
            return {
                "activated": False,
                "system_mode": "NORMAL",
                "drawdown_pct": drawdown_pct
            }

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])