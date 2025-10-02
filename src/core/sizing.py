# Sizing logic using house_money
from decimal import Decimal
from .house_money import compute

def trade_bank(nav: Decimal, day_profit_pct: Decimal) -> Decimal:
    # Use house_money for risk sizing
    return compute(nav, day_profit_pct)

LEVERAGE_CAP = 50
