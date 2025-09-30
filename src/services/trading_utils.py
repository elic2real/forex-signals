"""Canonical trading utility functions for OANDA FIFO compliance"""

import structlog
import math
from typing import Optional, Dict, Any

logger = structlog.get_logger()

# Trading constants
JPY_PIP_SIZE = 0.01  # 1 pip = 0.01 for JPY pairs
STANDARD_PIP_SIZE = 0.0001  # 1 pip = 0.0001 for other pairs
JPY_PRECISION = 3  # 150.123
STANDARD_PRECISION = 5  # 1.12345
MIN_TRADE_SIZE = 1  # OANDA minimum is 1 unit

# Global state for print_once to avoid log spam
_printed_messages = set()

def print_once(message: str, level: str = "info") -> None:
    """Print message only once to avoid log spam"""
    if message not in _printed_messages:
        _printed_messages.add(message)
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)

def validate_numeric(value: Any, name: str = "value", allow_zero: bool = True) -> float:
    """Validate and convert numeric value with safety checks"""
    try:
        if value is None:
            raise ValueError(f"{name} cannot be None")
        
        numeric_value = float(value)
        
        if not math.isfinite(numeric_value):
            raise ValueError(f"{name} must be finite (got {numeric_value})")
        
        if not allow_zero and numeric_value == 0:
            raise ValueError(f"{name} cannot be zero")
            
        return numeric_value
        
    except (TypeError, ValueError) as e:
        print_once(f"Invalid numeric value for {name}: {value} - {str(e)}", "error")
        return 0.0

def safe_round(value: float, precision: int) -> float:
    """Safely round a value with validation"""
    try:
        validated = validate_numeric(value, "round_value")
        if validated == 0.0:
            return 0.0
        return round(validated, precision)
    except Exception as e:
        print_once(f"Rounding failed for {value}: {str(e)}", "error")
        return 0.0

def pip_size_for(instrument: str) -> float:
    """Get pip size for instrument (canonical)"""
    if "JPY" in instrument:
        return JPY_PIP_SIZE
    return STANDARD_PIP_SIZE

def oanda_price_precision(instrument: str) -> int:
    """Get price precision for instrument (canonical)"""
    if "JPY" in instrument:
        return JPY_PRECISION
    return STANDARD_PRECISION

def oanda_min_trade_size(instrument: str) -> int:
    """Get minimum trade size for instrument (canonical)"""
    return MIN_TRADE_SIZE

def calculate_pip_value(instrument: str, units: float, account_currency: str = "USD") -> float:
    """Calculate pip value for position sizing (canonical)"""
    if not math.isfinite(units) or abs(units) < 1:
        return 0.0
        
    pip_size = pip_size_for(instrument)
    
    # For USD-based accounts, simplified calculation
    if account_currency == "USD":
        if "USD" == instrument[:3]:  # USD/XXX
            return pip_size * abs(units)
        elif "USD" == instrument[4:]:  # XXX/USD
            return pip_size * abs(units)
        else:  # Cross pairs - approximate
            return pip_size * abs(units)
    
    return pip_size * abs(units)

def calculate_correct_position_size(
    account_balance: float,
    risk_fraction: float,
    stop_loss_pips: float,
    instrument: str
) -> int:
    """Calculate position size based on risk management (canonical)"""
    if not all(math.isfinite(x) for x in [account_balance, risk_fraction, stop_loss_pips]):
        print_once("Invalid inputs to position sizing", "error")
        return 0
    
    if account_balance <= 0 or risk_fraction <= 0 or stop_loss_pips <= 0:
        return 0
    
    # Risk amount
    risk_amount = account_balance * risk_fraction
    
    # Pip value per unit
    pip_value = calculate_pip_value(instrument, 1.0)
    
    # Position size
    if pip_value > 0:
        position_size = int(risk_amount / (stop_loss_pips * pip_value))
        
        # Ensure minimum trade size
        min_size = oanda_min_trade_size(instrument)
        if position_size < min_size:
            print_once(f"Position size {position_size} below minimum {min_size}", "warning")
            return 0
            
        return position_size
    
    return 0

def verify_trade_will_be_profitable(
    entry_price: float,
    stop_loss_price: float,
    take_profit_price: float,
    spread: float,
    instrument: str,
    side: str
) -> bool:
    """Verify trade meets minimum profitability requirements (canonical)"""
    if not all(math.isfinite(x) for x in [entry_price, stop_loss_price, take_profit_price, spread]):
        return False
    
    pip_size = pip_size_for(instrument)
    spread_pips = spread / pip_size
    
    # Ensure minimum 10 pip profit after spread
    if side.upper() == "BUY":
        profit_pips = (take_profit_price - entry_price) / pip_size
        loss_pips = (entry_price - stop_loss_price) / pip_size
    else:  # SELL
        profit_pips = (entry_price - take_profit_price) / pip_size
        loss_pips = (stop_loss_price - entry_price) / pip_size
    
    # Profit floor: minimum 10 pips after spread
    net_profit_pips = profit_pips - spread_pips
    
    if net_profit_pips < 10:
        print_once(f"Trade below profit floor: {net_profit_pips:.1f} pips", "warning")
        return False
    
    # Risk/reward validation
    if loss_pips <= 0 or profit_pips / loss_pips < 1.0:
        print_once("Poor risk/reward ratio", "warning")
        return False
    
    return True

def get_account_balance() -> float:
    """Get account balance - to be implemented with OANDA client (canonical)"""
    # This would be implemented by the OANDA client in the actual system
    print_once("get_account_balance needs OANDA client implementation", "warning")
    return 10000.0  # Mock for development
