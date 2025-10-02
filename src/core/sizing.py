"""
System 2.1: Decimal Precision Position Sizing & Risk Management
Implementation of Requirement 1: DECIMAL PRECISION for all sizing calculations
"""

from decimal import Decimal, ROUND_DOWN, getcontext
from typing import Dict, Any, Tuple, Optional
from enum import Enum
import math
from .house_money import compute

# Set high precision for all decimal operations
getcontext().prec = 28

class LeverageLimit(Enum):
    MAX_LEVERAGE = Decimal('50.0')
    KELLY_LITE_CAP = Decimal('0.25')  # 25% max Kelly fraction

def trade_bank(nav: Decimal, day_profit_pct: Decimal) -> Decimal:
    # Use house_money for risk sizing
    return compute(nav, day_profit_pct)

LEVERAGE_CAP = 50

class PositionSizer:
    """
    Production-grade position sizing with Decimal precision
    Implements T.1: Test_Sizing_Precision requirements
    """
    
    def __init__(self, account_balance: Decimal, max_risk_per_trade: Decimal = Decimal('0.02')):
        self.account_balance = account_balance
        self.max_risk_per_trade = max_risk_per_trade  # 2% default
    
    def calculate_position_size(self, 
                              instrument: str,
                              entry_price: Decimal,
                              stop_loss: Decimal,
                              kelly_fraction: Optional[Decimal] = None,
                              gssi_score: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Calculate position size using Decimal precision
        
        Returns:
            Final Units = floor(min(units_risk, units_notional))
        """
        from src.core.trace_logger import system_logger
        
        # Calculate risk per pip in account currency
        pip_value = self._get_pip_value(instrument, entry_price)
        stop_distance_pips = abs(entry_price - stop_loss) * Decimal('10000')  # Assuming 4-decimal instruments
        
        # Risk-based sizing
        risk_amount = self.account_balance * self.max_risk_per_trade
        units_risk = risk_amount / (stop_distance_pips * pip_value)
        
        # Notional-based sizing (leverage limit)
        notional_value = entry_price * units_risk
        max_notional = self.account_balance * LeverageLimit.MAX_LEVERAGE.value
        units_notional = max_notional / entry_price
        
        # Kelly-Lite adjustment if provided
        kelly_capped = kelly_fraction
        if kelly_fraction:
            kelly_capped = min(kelly_fraction, LeverageLimit.KELLY_LITE_CAP.value)
            units_risk = units_risk * kelly_capped
        
        # GSSI dynamic adjustment (F.1)
        if gssi_score:
            gssi_multiplier = self._calculate_gssi_multiplier(gssi_score)
            units_risk = units_risk * gssi_multiplier
        
        # Final calculation: floor(min(units_risk, units_notional))
        final_units = min(units_risk, units_notional).quantize(Decimal('1'), rounding=ROUND_DOWN)
        
        sizing_data = {
            "instrument": instrument,
            "entry_price": float(entry_price),
            "stop_loss": float(stop_loss),
            "stop_distance_pips": float(stop_distance_pips),
            "units_risk": float(units_risk),
            "units_notional": float(units_notional),
            "final_units": float(final_units),
            "kelly_fraction": float(kelly_capped) if kelly_capped else None,
            "gssi_score": float(gssi_score) if gssi_score else None,
            "leverage_used": float(final_units * entry_price / self.account_balance)
        }
        
        # Log sizing calculation
        system_logger.logger.info("POSITION_SIZE_CALCULATED", **sizing_data)
        
        return {
            "units": final_units,
            "leverage": sizing_data["leverage_used"],
            "sizing_breakdown": sizing_data
        }
    
    def _get_pip_value(self, instrument: str, price: Decimal) -> Decimal:
        """Calculate pip value in account currency"""
        # Simplified - in production, this would use real-time conversion rates
        base_currency = instrument[:3]
        quote_currency = instrument[3:]
        
        if quote_currency == "USD":
            return Decimal('1.0')  # 1 pip = $1 for standard lot
        else:
            # For cross pairs, approximate conversion
            return Decimal('1.0') / price * Decimal('10000')
    
    def _calculate_gssi_multiplier(self, gssi_score: Decimal) -> Decimal:
        """
        GSSI/CAR dynamic sizing adjustment (F.1)
        Higher GSSI = Lower position size
        """
        if gssi_score >= Decimal('0.8'):
            return Decimal('0.5')  # Reduce to 50%
        elif gssi_score >= Decimal('0.6'):
            return Decimal('0.75')  # Reduce to 75%
        else:
            return Decimal('1.0')  # No reduction

class AddToWinnersManager:
    """
    Add-to-Winners state machine with Decimal precision
    Implements T.1: Test_Add_to_Winners_Eligibility
    """
    
    def __init__(self):
        self.state = "initial"  # initial -> add_1 -> add_2 -> maxed
        self.progress_threshold = Decimal('0.7')  # +0.7R
        self.drawdown_limit = Decimal('0.25')    # 0.25R max drawdown
    
    def check_add_eligibility(self, 
                            current_progress: Decimal, 
                            max_drawdown: Decimal,
                            initial_risk: Decimal) -> Dict[str, Any]:
        """
        Check if position is eligible for adding
        
        Conditions:
        - progress >= +0.7R
        - drawdown <= 0.25R
        """
        from src.core.trace_logger import system_logger
        
        eligible = (current_progress >= self.progress_threshold and 
                   max_drawdown <= self.drawdown_limit)
        
        if eligible and self.state == "initial":
            self.state = "add_1"
            new_be_price = self._calculate_weighted_be_reset(current_progress, initial_risk)
        else:
            new_be_price = None
        
        result = {
            "eligible": eligible,
            "current_state": self.state,
            "progress": float(current_progress),
            "drawdown": float(max_drawdown),
            "new_breakeven": float(new_be_price) if new_be_price else None
        }
        
        system_logger.logger.info("ADD_TO_WINNERS_CHECK", **result)
        return result
    
    def _calculate_weighted_be_reset(self, progress: Decimal, initial_risk: Decimal) -> Decimal:
        """Calculate weighted breakeven reset price"""
        # Simplified weighted BE calculation
        return initial_risk * progress * Decimal('0.5')  # Move BE to +50% of progress

class QuantileATRCalculator:
    """
    Quantile-ATR SL width calculation with rolling time window
    Implements R.1: Quantile-ATR verification
    """
    
    def __init__(self, lookback_periods: int = 100):
        self.lookback_periods = lookback_periods
        self.atr_history = []
    
    def calculate_quantile_sl_width(self, 
                                  current_atr: Decimal, 
                                  quantile: Decimal = Decimal('0.75')) -> Decimal:
        """
        Calculate SL width using quantile-based ATR
        Uses rolling time window to prevent over-optimization
        """
        self.atr_history.append(current_atr)
        if len(self.atr_history) > self.lookback_periods:
            self.atr_history.pop(0)
        
        if len(self.atr_history) < 10:  # Minimum history required
            return current_atr * Decimal('1.5')  # Default fallback
        
        # Calculate quantile
        sorted_atr = sorted(self.atr_history)
        quantile_index = int(len(sorted_atr) * quantile)
        quantile_atr = sorted_atr[quantile_index]
        
        return quantile_atr * Decimal('1.2')  # 20% buffer
