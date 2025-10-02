# House-Money strategy logic (preserved, do not modify semantics)
from decimal import Decimal

def compute(nav: Decimal, day_profit_pct: Decimal) -> Decimal:
    # House-Money: base + profit allocation
    base = nav * Decimal('0.7')
    profit = nav * Decimal('0.3')
    if day_profit_pct < Decimal('0.02'):
        # Only base at risk
        allocation = base
    elif day_profit_pct < Decimal('0.035'):
        # Only profit at risk
        allocation = profit
    else:
        # Gradually re-add base
        allocation = profit + (base * (day_profit_pct - Decimal('0.035')) / Decimal('0.015'))
        allocation = min(nav, allocation)
    return allocation
